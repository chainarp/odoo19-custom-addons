// itx_ai_helm/static/src/components/terminal/terminal.js
// Terminal Component with Bus.bus (Primary) + Long Polling (Fallback)

/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { TerminalConnectionManager } from "../../services/terminal_connection";

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
        this.notification = useService("notification");
        this.terminalRef = useRef("terminal");

        // Bus service for real-time output (Primary mode)
        try {
            this.busService = useService("bus_service");
        } catch (e) {
            console.warn('[Terminal] bus_service not available, will use Long Polling');
            this.busService = null;
        }

        // Resume Session: เช็ค localStorage ว่ามี session เก่าหรือไม่
        const savedSessionId = this.getSavedSessionId();

        this.state = useState({
            connected: false,
            session_id: savedSessionId,
            loading: true,
            connectionMode: null  // 'websocket' | 'polling' | null
        });

        this.terminal = null;
        this.fitAddon = null;
        this.connectionManager = null;

        onMounted(() => {
            this.initTerminal();
        });

        onWillUnmount(() => {
            // Cleanup
            if (this.connectionManager) {
                // Don't destroy session to allow resume
                this.connectionManager.disconnect(false);
            }

            if (this.resizeHandler) {
                window.removeEventListener('resize', this.resizeHandler);
            }

            if (this.terminal) {
                this.terminal.dispose();
                this.terminal = null;
            }
        });
    }

    getSavedSessionId() {
        /**
         * ดึง session_id ที่เก็บไว้จาก localStorage
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
         */
        try {
            // ตรวจสอบว่า xterm.js loaded แล้วหรือยัง
            if (!window.Terminal || !window.FitAddon) {
                throw new Error('xterm.js not loaded. Please check __manifest__.py assets.');
            }

            // สร้าง terminal instance
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

            // เพิ่ม fit addon
            this.fitAddon = new window.FitAddon.FitAddon();
            this.terminal.loadAddon(this.fitAddon);

            // เปิด terminal ใน DOM
            const terminalElement = this.terminalRef.el;
            if (!terminalElement) {
                throw new Error('Terminal container not found.');
            }

            this.terminal.open(terminalElement);

            // รอ 1 tick ให้ DOM update ก่อน fit
            await new Promise(resolve => setTimeout(resolve, 0));
            this.fitAddon.fit();

            // แสดง welcome message
            const cmd = this.terminalCommand;
            const cmdName = cmd === 'claude' ? 'Claude CLI' : cmd === 'bash' ? 'Bash' : cmd;
            this.terminal.writeln(`\x1b[1;36m\u{1F680} Connecting to ${cmdName}...\x1b[0m\r\n`);

            // เชื่อมต่อกับ backend ผ่าน ConnectionManager
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
         * เชื่อมต่อ terminal session ผ่าน ConnectionManager
         */
        try {
            // Create connection manager with bus_service for real-time output
            this.connectionManager = new TerminalConnectionManager({
                sessionId: this.state.session_id,
                command: this.terminalCommand,
                busService: this.busService,  // Inject bus_service for real-time mode

                onOutput: (data) => {
                    // Write output to terminal
                    if (this.terminal) {
                        this.terminal.write(data);
                    }
                },

                onConnect: (info) => {
                    // Connected
                    this.state.session_id = info.sessionId;
                    this.state.connected = true;

                    // Save session ID
                    this.saveSessionId(info.sessionId);

                    // Show status
                    if (info.isResumed && info.history) {
                        this.terminal.writeln(`\x1b[1;33m\u21BB Resumed session\x1b[0m (${info.sessionId.slice(0, 8)}...)\r\n`);
                        this.terminal.writeln(`\x1b[2m\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\x1b[0m\r\n`);
                        this.terminal.write(info.history);
                        this.terminal.writeln(`\x1b[2m\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\x1b[0m\r\n`);
                    } else {
                        this.terminal.writeln(`\x1b[1;32m\u2713 Connected\x1b[0m (Session: ${info.sessionId.slice(0, 8)}...)\r\n`);
                    }

                    this.terminal.focus();
                },

                onDisconnect: () => {
                    // Disconnected
                    this.state.connected = false;
                    console.log('[Terminal] Disconnected');
                },

                onModeChange: (mode) => {
                    // Connection mode changed
                    this.state.connectionMode = mode;
                    console.log('[Terminal] Connection mode:', mode);
                }
            });

            // Connect
            const connected = await this.connectionManager.connect();

            if (!connected) {
                throw new Error('Failed to connect to terminal');
            }

        } catch (error) {
            this.terminal.writeln(`\x1b[1;31m\u2717 Connection failed: ${error.message}\x1b[0m\r\n`);
            console.error('Terminal connection error:', error);

            // If resume failed, clear session and retry
            if (this.state.session_id) {
                this.clearSavedSessionId();
                this.state.session_id = null;
                this.terminal.writeln(`\x1b[1;33m\u21BB Creating new session...\x1b[0m\r\n`);
                return this.connectSession();
            }

            throw error;
        }
    }

    setupEventHandlers() {
        /**
         * ตั้งค่า event handlers สำหรับ terminal
         */

        // Handle keyboard input
        this.terminal.onData(async (data) => {
            if (!this.state.connected || !this.connectionManager) {
                return;
            }

            try {
                await this.connectionManager.sendInput(data);
            } catch (error) {
                console.error('Write error:', error);
            }
        });

        // Handle terminal resize
        this.terminal.onResize(async ({ cols, rows }) => {
            if (!this.state.connected || !this.connectionManager) {
                return;
            }

            try {
                await this.connectionManager.sendResize(rows, cols);
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
         */
        if (this.connectionManager) {
            await this.connectionManager.disconnect(true);
        }

        // ลบ session_id จาก localStorage
        this.clearSavedSessionId();

        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }

        if (this.terminal) {
            this.terminal.dispose();
            this.terminal = null;
        }

        this.state.connected = false;
        this.state.session_id = null;
        this.state.connectionMode = null;
    }

    /**
     * Get connection mode display text
     */
    getConnectionModeText() {
        if (this.state.connectionMode === 'bus') {
            return 'Bus (Real-time)';
        } else if (this.state.connectionMode === 'websocket') {
            return 'WebSocket';
        } else if (this.state.connectionMode === 'polling') {
            return 'Polling';
        }
        return '';
    }

    /**
     * Get connection mode badge class
     */
    getConnectionModeBadgeClass() {
        if (this.state.connectionMode === 'bus') {
            return 'bg-success';  // Green for Bus (real-time)
        } else if (this.state.connectionMode === 'websocket') {
            return 'bg-primary';  // Blue for WebSocket
        } else if (this.state.connectionMode === 'polling') {
            return 'bg-warning text-dark';  // Yellow for Polling
        }
        return 'bg-secondary';
    }
}

// Register as action
registry.category("actions").add("itx_ai_helm.terminal", ClaudeTerminal);
