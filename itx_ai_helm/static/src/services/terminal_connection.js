// itx_ai_helm/static/src/services/terminal_connection.js
// Connection Manager with Bus.bus (Primary) + Long Polling (Fallback)

/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

/**
 * TerminalConnectionManager
 *
 * Manages terminal connection with Bus.bus primary and Long Polling fallback.
 *
 * Connection Strategy:
 * 1. Connect via JSON-RPC to get session_id and bus_channel
 * 2. If bus available -> subscribe to bus channel for output (real-time)
 * 3. If bus not available -> fallback to Long Polling for output
 * 4. Input always via JSON-RPC POST
 */
export class TerminalConnectionManager {
    /**
     * @param {Object} options
     * @param {string} options.sessionId - Optional session ID for resume
     * @param {string} options.command - Command to run (default: 'bash')
     * @param {Function} options.onOutput - Callback for terminal output
     * @param {Function} options.onConnect - Callback when connected
     * @param {Function} options.onDisconnect - Callback when disconnected
     * @param {Function} options.onModeChange - Callback when connection mode changes
     * @param {Object} options.busService - Odoo bus_service (optional, for Bus.bus mode)
     */
    constructor(options = {}) {
        this.sessionId = options.sessionId || null;
        this.command = options.command || 'bash';
        this.onOutput = options.onOutput || (() => {});
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onModeChange = options.onModeChange || (() => {});

        // Bus service (injected from component)
        this.busService = options.busService || null;

        // Connection state
        this.connected = false;
        this.mode = null; // 'bus' | 'polling' | null
        this.busChannel = null;
        this.isPolling = false;

        // Input batching for better performance
        this._inputBuffer = '';
        this._inputTimeout = null;
        this._inputDelay = 5; // ms - batch inputs within 5ms window

        // For backward compatibility (legacy WebSocket - not used)
        this.ws = null;
        this.wsReconnectAttempts = 0;
        this.maxWsReconnectAttempts = 3;
        this.reconnectDelay = 1000;
        this.wsUpgradeCheckInterval = null;
        this.wsUpgradeCheckDelay = 60000;
        this.pingInterval = null;
        this.pingDelay = 30000;
    }

    /**
     * Connect to terminal
     * Uses Bus.bus if available, fallback to Long Polling
     *
     * @returns {Promise<boolean>} - True if connected successfully
     */
    async connect() {
        console.log('[TerminalConnection] Starting connection...');

        try {
            // Connect via JSON-RPC
            const result = await rpc("/terminal/connect", {
                session_id: this.sessionId,
                command: this.command,
                use_bus: !!this.busService  // Request bus mode if bus_service available
            });

            if (!result.success) {
                console.error('[TerminalConnection] Connect failed:', result.error);
                return false;
            }

            this.sessionId = result.session_id;
            this.busChannel = result.bus_channel;
            this.connected = true;

            // Notify caller
            this.onConnect({
                sessionId: result.session_id,
                isResumed: result.is_resumed,
                history: result.history
            });

            // Choose output mode: Bus or Polling
            if (result.use_bus && this.busService) {
                // Use Bus.bus for output (real-time)
                this._startBusSubscription();
                this.mode = 'bus';
                this.onModeChange('bus');
                console.log('[TerminalConnection] Connected via Bus.bus (real-time)');
            } else {
                // Fallback to Long Polling
                this._startPollingLoop();
                this.mode = 'polling';
                this.onModeChange('polling');
                console.log('[TerminalConnection] Connected via Long Polling (fallback)');
            }

            return true;

        } catch (e) {
            console.error('[TerminalConnection] Connect error:', e);
            return false;
        }
    }

    /**
     * Start Bus.bus subscription for real-time output
     */
    _startBusSubscription() {
        if (!this.busService || !this.busChannel) {
            console.warn('[TerminalConnection] Bus service or channel not available');
            return;
        }

        try {
            // Add channel to listen
            this.busService.addChannel(this.busChannel);

            // Subscribe to terminal_output messages
            this.busService.subscribe('terminal_output', (payload) => {
                // Only process output for our session
                if (payload.session_id === this.sessionId) {
                    this.onOutput(payload.output);
                }
            });

            console.log(`[TerminalConnection] Subscribed to bus channel: ${this.busChannel}`);

        } catch (e) {
            console.error('[TerminalConnection] Bus subscription error:', e);
            // Fallback to polling
            this._startPollingLoop();
            this.mode = 'polling';
            this.onModeChange('polling');
        }
    }

    /**
     * Stop Bus.bus subscription
     */
    _stopBusSubscription() {
        // Note: Odoo bus_service doesn't have removeChannel/unsubscribe in standard API
        // The subscription will be cleaned up when the component is destroyed
        this.busChannel = null;
    }

    /**
     * Start Long Polling loop for output
     */
    _startPollingLoop() {
        if (this.isPolling) {
            return;
        }

        this.isPolling = true;
        this._poll();
    }

    /**
     * Long Polling loop
     */
    async _poll() {
        if (!this.isPolling || !this.connected || this.mode !== 'polling') {
            return;
        }

        try {
            const result = await rpc("/terminal/poll", {
                session_id: this.sessionId,
                timeout: 30
            });

            if (result.success && result.output) {
                this.onOutput(result.output);
            }

            // Continue polling immediately
            setTimeout(() => this._poll(), 0);

        } catch (e) {
            console.error('[TerminalConnection] Poll error:', e);

            // Retry after delay
            setTimeout(() => this._poll(), 2000);
        }
    }

    /**
     * Stop Long Polling
     */
    _stopPolling() {
        this.isPolling = false;
    }

    /**
     * Send input to terminal (always via JSON-RPC)
     * Uses batching to reduce HTTP overhead
     *
     * @param {string} data - Input data
     */
    async sendInput(data) {
        if (!this.connected) {
            return false;
        }

        // Check if this is a special key that should be sent immediately
        // Enter (\r), Ctrl+C (\x03), Ctrl+D (\x04), Escape (\x1b), Arrow keys, etc.
        const isSpecialKey = data.length === 1 && data.charCodeAt(0) < 32;
        const isEscapeSequence = data.startsWith('\x1b');

        if (isSpecialKey || isEscapeSequence) {
            // Flush any pending input first, then send this immediately
            if (this._inputBuffer) {
                await this._flushInputBuffer();
            }
            // Send special key immediately
            try {
                await rpc("/terminal/write", {
                    session_id: this.sessionId,
                    data
                });
            } catch (e) {
                console.error('[TerminalConnection] Send input error:', e);
            }
            return true;
        }

        // Regular character - add to buffer
        this._inputBuffer += data;

        // Clear existing timeout
        if (this._inputTimeout) {
            clearTimeout(this._inputTimeout);
        }

        // Set timeout to flush buffer
        this._inputTimeout = setTimeout(() => {
            this._flushInputBuffer();
        }, this._inputDelay);

        return true;
    }

    /**
     * Flush input buffer - send all buffered input at once
     */
    async _flushInputBuffer() {
        if (!this._inputBuffer || !this.connected) {
            return;
        }

        const data = this._inputBuffer;
        this._inputBuffer = '';
        this._inputTimeout = null;

        try {
            await rpc("/terminal/write", {
                session_id: this.sessionId,
                data
            });
        } catch (e) {
            console.error('[TerminalConnection] Send input error:', e);
        }
    }

    /**
     * Send resize event to terminal (always via JSON-RPC)
     *
     * @param {number} rows - Number of rows
     * @param {number} cols - Number of columns
     */
    async sendResize(rows, cols) {
        if (!this.connected) {
            return false;
        }

        try {
            await rpc("/terminal/resize", {
                session_id: this.sessionId,
                rows,
                cols
            });
            return true;
        } catch (e) {
            console.error('[TerminalConnection] Resize error:', e);
            return false;
        }
    }

    /**
     * Disconnect from terminal
     *
     * @param {boolean} destroySession - Whether to destroy the backend session
     */
    async disconnect(destroySession = false) {
        this.connected = false;

        // Stop bus subscription
        this._stopBusSubscription();

        // Stop polling
        this._stopPolling();

        // Stop ping (legacy)
        this._stopPing();

        // Stop WebSocket upgrade check (legacy)
        if (this.wsUpgradeCheckInterval) {
            clearInterval(this.wsUpgradeCheckInterval);
            this.wsUpgradeCheckInterval = null;
        }

        // Close WebSocket (legacy)
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        // Destroy backend session if requested
        if (destroySession && this.sessionId) {
            try {
                await rpc("/terminal/disconnect", {
                    session_id: this.sessionId
                });
            } catch (e) {
                console.error('[TerminalConnection] Disconnect error:', e);
            }
        }

        this.mode = null;
        this.onDisconnect();
    }

    // ============================================================
    // Legacy methods (for backward compatibility, not actively used)
    // ============================================================

    async _tryWebSocket() {
        // WebSocket not supported in Odoo 19 without custom implementation
        // Always return false to use Bus.bus or Polling
        return false;
    }

    async _handleWsDisconnect() {
        // Not used - kept for backward compatibility
    }

    async _switchToPolling() {
        this._startPollingLoop();
        this.mode = 'polling';
        this.onModeChange('polling');
    }

    async _startPolling() {
        this._startPollingLoop();
        return true;
    }

    _startWsUpgradeCheck() {
        // Not used - kept for backward compatibility
    }

    _startPing() {
        // Not used - kept for backward compatibility
    }

    _stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    /**
     * Get current connection mode
     *
     * @returns {'bus' | 'polling' | null}
     */
    getMode() {
        return this.mode;
    }

    /**
     * Check if connected
     *
     * @returns {boolean}
     */
    isConnected() {
        return this.connected;
    }

    /**
     * Get session ID
     *
     * @returns {string | null}
     */
    getSessionId() {
        return this.sessionId;
    }
}
