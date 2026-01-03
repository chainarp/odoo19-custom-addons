// itx_ai_helm/static/src/components/terminal/terminal.js
// Long Polling Implementation (แทน WebSocket)

/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";  // Import rpc โดยตรง (Odoo 16+)

export class ClaudeTerminal extends Component {
    static template = "itx_ai_helm.ClaudeTerminal";
    static props = {
        session_id: { type: String, optional: true },
        command: { type: String, optional: true }
    };

    get terminalCommand() {
        // Default เป็น bash ถ้าไม่ระบุ (เพราะ claude ใช้ memory เยอะ)
        return this.props.command || 'bash';
    }

    setup() {
        // ไม่ต้องใช้ useService("rpc") แล้ว - ใช้ import rpc แทน
        this.notification = useService("notification");
        this.terminalRef = useRef("terminal");

        // ✅ Resume Session: เช็ค localStorage ว่ามี session เก่าหรือไม่
        const savedSessionId = this.getSavedSessionId();

        this.state = useState({
            connected: false,
            // ถ้ามี session เก่า → ลองใช้ต่อ, ไม่มี → สร้างใหม่
            session_id: savedSessionId,
            loading: true
        });

        this.terminal = null;
        this.fitAddon = null;
        this.pollInterval = null;
        this.isPolling = false;

        onMounted(() => {
            this.initTerminal();
        });

        onWillUnmount(() => {
            // ไม่ cleanup session เพื่อให้ resume ได้
            this.stopPolling();

            // ลบ event listener
            if (this.resizeHandler) {
                window.removeEventListener('resize', this.resizeHandler);
            }

            // ทำลาย terminal UI (แต่ไม่ทำลาย backend session)
            if (this.terminal) {
                this.terminal.dispose();
                this.terminal = null;
            }
        });
    }

    getSavedSessionId() {
        /**
         * ดึง session_id ที่เก็บไว้จาก localStorage
         *
         * Key pattern: terminal_session_{command}
         * เช่น: terminal_session_bash, terminal_session_claude
         */
        try {
            const key = `terminal_session_${this.terminalCommand}`;
            return localStorage.getItem(key);
        } catch (e) {
            console.warn('Could not read localStorage:', e);
            return null;
        }
    }

    saveSessionId(sessionId) {
        /**
         * เก็บ session_id ลง localStorage
         */
        try {
            const key = `terminal_session_${this.terminalCommand}`;
            localStorage.setItem(key, sessionId);
        } catch (e) {
            console.warn('Could not save to localStorage:', e);
        }
    }

    clearSavedSessionId() {
        /**
         * ลบ session_id ออกจาก localStorage
         */
        try {
            const key = `terminal_session_${this.terminalCommand}`;
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('Could not clear localStorage:', e);
        }
    }

    async initTerminal() {
        /**
         * สร้าง terminal instance และเชื่อมต่อกับ backend
         *
         * สิ่งสำคัญ:
         * - ใช้ window.Terminal และ window.FitAddon (global จาก xterm.js)
         * - ห้าม import เพราะ Odoo load เป็น global scripts
         */
        try {
            // ตรวจสอบว่า xterm.js loaded แล้วหรือยัง
            if (!window.Terminal || !window.FitAddon) {
                throw new Error('xterm.js not loaded. Please check __manifest__.py assets.');
            }

            // สร้าง terminal instance (ใช้ global window.Terminal)
            this.terminal = new window.Terminal({
                cursorBlink: true,
                fontSize: 14,
                fontFamily: 'Fira Code, Consolas, monospace',
                theme: {
                    background: '#1e1e1e',
                    foreground: '#d4d4d4',
                    cursor: '#aeafad',
                    selection: '#264f78',
                    black: '#000000',
                    red: '#cd3131',
                    green: '#0dbc79',
                    yellow: '#e5e510',
                    blue: '#2472c8',
                    magenta: '#bc3fbc',
                    cyan: '#11a8cd',
                    white: '#e5e5e5',
                    brightBlack: '#666666',
                    brightRed: '#f14c4c',
                    brightGreen: '#23d18b',
                    brightYellow: '#f5f543',
                    brightBlue: '#3b8eea',
                    brightMagenta: '#d670d6',
                    brightCyan: '#29b8db',
                    brightWhite: '#e5e5e5'
                },
                scrollback: 1000,
                rightClickSelectsWord: true
            });

            // เพิ่ม fit addon (ใช้ global window.FitAddon)
            this.fitAddon = new window.FitAddon.FitAddon();
            this.terminal.loadAddon(this.fitAddon);

            // เปิด terminal ใน DOM
            const terminalElement = this.terminalRef.el;
            if (!terminalElement) {
                console.error('terminalRef:', this.terminalRef);
                throw new Error('Terminal container not found. Check t-ref="terminal" in XML template.');
            }

            this.terminal.open(terminalElement);

            // รอ 1 tick ให้ DOM update ก่อน fit
            await new Promise(resolve => setTimeout(resolve, 0));
            this.fitAddon.fit();

            // แสดง welcome message
            const cmd = this.terminalCommand;
            const cmdName = cmd === 'claude' ? 'Claude CLI' : cmd === 'bash' ? 'Bash' : cmd;
            this.terminal.writeln(`\x1b[1;36m🚀 Connecting to ${cmdName}...\x1b[0m\r\n`);

            // เชื่อมต่อกับ backend
            await this.connectSession();

            // Setup event handlers
            this.setupEventHandlers();

            // Handle window resize
            this.resizeHandler = this.handleResize.bind(this);
            window.addEventListener('resize', this.resizeHandler);

            this.state.loading = false;

        } catch (error) {
            console.error('Terminal init error:', error);
            this.notification.add(`Terminal error: ${error.message}`, {
                type: 'danger'
            });
            this.state.loading = false;
        }
    }

    async connectSession() {
        /**
         * สร้างหรือเชื่อมต่อ terminal session (Resume-enabled)
         *
         * Flow:
         * 1. ถ้ามี session_id เก่า → ลอง connect
         * 2. ถ้า connect สำเร็จ → แสดง history (resume) หรือ welcome (new)
         * 3. ถ้า connect ไม่ได้ → สร้างใหม่
         */
        try {
            const result = await rpc("/terminal/connect", {
                session_id: this.state.session_id,
                command: this.terminalCommand
            });

            if (result.success) {
                this.state.session_id = result.session_id;
                this.state.connected = true;

                // บันทึก session_id ลง localStorage
                this.saveSessionId(result.session_id);

                // แสดง message และ history ตามสถานะ
                if (result.is_resumed && result.history) {
                    // Resume session → แสดง history
                    this.terminal.writeln(`\x1b[1;33m↻ Resumed session\x1b[0m (${result.session_id.slice(0, 8)}...)\r\n`);
                    this.terminal.writeln(`\x1b[2m─────────────────────────────────\x1b[0m\r\n`);

                    // เขียน history (ไม่ใส่ \r\n เพราะ history มีอยู่แล้ว)
                    this.terminal.write(result.history);

                    this.terminal.writeln(`\x1b[2m─────────────────────────────────\x1b[0m\r\n`);
                } else {
                    // New session → แสดง welcome
                    this.terminal.writeln(`\x1b[1;32m✓ Connected\x1b[0m (Session: ${result.session_id.slice(0, 8)}...)\r\n`);
                }

                this.terminal.focus();

                // เริ่ม polling
                this.startPolling();
            } else {
                throw new Error(result.error || 'Failed to create session');
            }
        } catch (error) {
            this.terminal.writeln(`\x1b[1;31m✗ Connection failed: ${error.message}\x1b[0m\r\n`);
            console.error('Terminal connection error:', error);

            // ถ้า resume ไม่สำเร็จ → ลบ session_id เก่าแล้วลองใหม่
            if (this.state.session_id) {
                this.clearSavedSessionId();
                this.state.session_id = null;
                this.terminal.writeln(`\x1b[1;33m↻ Creating new session...\x1b[0m\r\n`);

                // Retry without session_id
                return this.connectSession();
            }

            throw error;
        }
    }

    startPolling() {
        /**
         * เริ่ม Long Polling เพื่อรับ output จาก terminal
         *
         * Long Polling ทำงานโดย:
         * 1. ส่ง request ไป /terminal/poll
         * 2. Server รอจนมี output ใหม่ (หรือ timeout)
         * 3. ได้ output แล้วแสดงใน terminal
         * 4. ส่ง request ใหม่ทันที (วนไปเรื่อยๆ)
         */
        if (this.isPolling) {
            return; // ป้องกัน double polling
        }

        this.isPolling = true;
        this.poll();
    }

    async poll() {
        /**
         * ส่ง polling request ไปรับ output
         * (เรียกตัวเองวนไปเรื่อยๆ จนกว่าจะ disconnect)
         */
        if (!this.isPolling || !this.state.connected) {
            return;
        }

        try {
            const result = await rpc("/terminal/poll", {
                session_id: this.state.session_id,
                timeout: 30  // รอสูงสุด 30 วินาที
            });

            if (result.success && result.output) {
                // แสดง output ใน terminal
                this.terminal.write(result.output);
            }

            // Poll ต่อทันที (ไม่ต้องรอ)
            // ใช้ setTimeout 0 เพื่อไม่ให้ block event loop
            setTimeout(() => this.poll(), 0);

        } catch (error) {
            console.error('Poll error:', error);

            // ถ้า error ให้รอ 2 วินาทีก่อน poll ใหม่
            setTimeout(() => this.poll(), 2000);
        }
    }

    stopPolling() {
        /**
         * หยุด polling (เช่น เมื่อ disconnect)
         */
        this.isPolling = false;
    }

    setupEventHandlers() {
        /**
         * ตั้งค่า event handlers สำหรับ terminal
         */

        // Handle keyboard input
        this.terminal.onData(async (data) => {
            if (!this.state.connected) {
                return;
            }

            try {
                // ส่ง input ไปยัง backend
                await rpc("/terminal/write", {
                    session_id: this.state.session_id,
                    data: data
                });
            } catch (error) {
                console.error('Write error:', error);
            }
        });

        // Handle terminal resize
        this.terminal.onResize(async ({ cols, rows }) => {
            if (!this.state.connected) {
                return;
            }

            try {
                await rpc("/terminal/resize", {
                    session_id: this.state.session_id,
                    rows: rows,
                    cols: cols
                });
            } catch (error) {
                console.error('Resize error:', error);
            }
        });
    }

    handleResize() {
        /**
         * จัดการเมื่อหน้าต่าง browser resize
         */
        if (this.fitAddon) {
            this.fitAddon.fit();
        }
    }

    clearTerminal() {
        /**
         * ล้าง terminal screen
         */
        if (this.terminal) {
            this.terminal.clear();
        }
    }

    async destroySession() {
        /**
         * ทำลาย session ทั้งหมด (frontend + backend)
         * เรียกเมื่อ user ต้องการ "New Terminal" จริงๆ
         */
        // หยุด polling
        this.stopPolling();

        // แจ้ง backend ว่าจะ disconnect
        if (this.state.session_id) {
            try {
                await rpc("/terminal/disconnect", {
                    session_id: this.state.session_id
                });
                // ลบ session_id จาก localStorage
                this.clearSavedSessionId();
            } catch (error) {
                console.error('Disconnect error:', error);
            }
        }

        // ลบ event listener
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }

        // ทำลาย terminal instance
        if (this.terminal) {
            this.terminal.dispose();
            this.terminal = null;
        }

        this.state.connected = false;
        this.state.session_id = null;
    }
}

// Register as action
registry.category("actions").add("itx_ai_helm.terminal", ClaudeTerminal);
