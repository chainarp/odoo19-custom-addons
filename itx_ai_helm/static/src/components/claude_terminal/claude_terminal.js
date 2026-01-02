// itx_ai_helm/static/src/components/claude_terminal/claude_terminal.js

/** @odoo-module **/

import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { AttachAddon } from 'xterm-addon-attach';

export class ClaudeTerminal extends Component {
    static template = "itx_ai_helm.ClaudeTerminal";

    setup() {
        this.terminal = null;
        this.websocket = null;

        onMounted(() => {
            this.initTerminal();
        });

        onWillUnmount(() => {
            this.cleanup();
        });
    }

    initTerminal() {
        // Create terminal
        this.terminal = new Terminal({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'Fira Code, monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#f0f0f0',
                selection: '#264f78',
                black: '#000000',
                red: '#cd3131',
                green: '#0dbc79',
                yellow: '#e5e510',
                blue: '#2472c8',
                magenta: '#bc3fbc',
                cyan: '#11a8cd',
                white: '#e5e5e5'
            }
        });

        // Add addons
        const fitAddon = new FitAddon();
        this.terminal.loadAddon(fitAddon);
        this.terminal.loadAddon(new WebLinksAddon());

        // Open terminal
        this.terminal.open(document.getElementById('terminal'));
        fitAddon.fit();

        // Connect WebSocket
        this.connectWebSocket();

        // Handle input
        this.terminal.onData(data => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({
                    type: 'input',
                    data: data
                }));
            }
        });

        // Handle resize
        this.terminal.onResize(({ cols, rows }) => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({
                    type: 'resize',
                    cols: cols,
                    rows: rows
                }));
            }
        });

        // Auto resize
        window.addEventListener('resize', () => fitAddon.fit());
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/terminal/ws`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            this.terminal.write('\r\n🚀 Connected to Claude CLI\r\n\r\n');
        };

        this.websocket.onmessage = (event) => {
            this.terminal.write(event.data);
        };

        this.websocket.onerror = (error) => {
            this.terminal.write('\r\n❌ Connection error\r\n');
        };

        this.websocket.onclose = () => {
            this.terminal.write('\r\n📡 Connection closed\r\n');
        };
    }

    cleanup() {
        if (this.websocket) {
            this.websocket.close();
        }
        if (this.terminal) {
            this.terminal.dispose();
        }
    }
}