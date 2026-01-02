// itx_ai_helm/static/src/components/ai_chat/ai_chat.js

/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class AIChatWidget extends Component {
    static template = "itx_ai_helm.AIChatWidget";
    static props = ["*"];

    setup() {
        this.notification = useService("notification");
        this.messageInput = useRef("messageInput");

        this.state = useState({
            messages: [],
            currentMessage: "",
            isLoading: false,
            conversationId: null,
        });

        onMounted(() => {
            this.loadOrCreateConversation();
        });
    }

    async loadOrCreateConversation() {
        try {
            const result = await rpc("/ai_helm/get_or_create_conversation", {});
            console.log("Conversation loaded:", result);
            this.state.conversationId = result.conversation_id;
            this.state.messages = result.messages || [];
            this.scrollToBottom();
        } catch (error) {
            console.error("Failed to load conversation3:", error);
            const errorMsg = error.message || error.data?.message || JSON.stringify(error);
            this.notification.add(`Failed to load conversation: ${errorMsg}`, {
                type: "danger",
            });
        }
    }

    async sendMessage() {
        if (!this.state.currentMessage.trim() || this.state.isLoading) {
            return;
        }

        const message = this.state.currentMessage;
        this.state.currentMessage = "";

        // Add user message
        const userMessage = {
            type: 'user',
            content: message,
            timestamp: new Date().toISOString(),
            status: 'complete'
        };
        this.state.messages.push(userMessage);

        // Add loading message
        const loadingMessage = {
            type: 'assistant',
            content: '...',
            timestamp: new Date().toISOString(),
            status: 'sending'
        };
        this.state.messages.push(loadingMessage);

        this.state.isLoading = true;
        this.scrollToBottom();

        try {
            const result = await rpc("/ai_helm/send_message", {
                conversation_id: this.state.conversationId,
                message: message
            });

            // Replace loading message with actual response
            this.state.messages[this.state.messages.length - 1] = {
                type: 'assistant',
                content: result.response,
                code_blocks: result.code_blocks || [],
                timestamp: new Date().toISOString(),
                status: 'complete'
            };

        } catch (error) {
            console.error("Failed to send message:", error);
            const errorMsg = error.message || error.data?.message || JSON.stringify(error);
            // Replace loading message with error
            this.state.messages[this.state.messages.length - 1] = {
                type: 'error',
                content: `Error: ${errorMsg}`,
                timestamp: new Date().toISOString(),
                status: 'error'
            };
        } finally {
            this.state.isLoading = false;
            this.scrollToBottom();
        }
    }

    onKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    async clearConversation() {
        if (confirm("Clear this conversation?")) {
            try {
                await rpc("/ai_helm/clear_conversation", {
                    conversation_id: this.state.conversationId
                });
                this.state.messages = [];
                this.notification.add("Conversation cleared", {
                    type: "success",
                });
            } catch (error) {
                this.notification.add("Failed to clear conversation", {
                    type: "danger",
                });
            }
        }
    }

    async copyCode(code) {
        try {
            await navigator.clipboard.writeText(code);
            this.notification.add("Code copied to clipboard", {
                type: "success",
            });
        } catch (error) {
            this.notification.add("Failed to copy code", {
                type: "danger",
            });
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            const chatContainer = document.querySelector('.ai-chat-messages');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
    }
}

registry.category("actions").add("itx_ai_helm.ai_chat", AIChatWidget);