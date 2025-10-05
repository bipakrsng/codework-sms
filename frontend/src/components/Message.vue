<template>
  <div class="d-flex vh-50 bg-light">
    <!-- LEFT: Search + Inbox -->
    <div class="col-4 border-end d-flex flex-column bg-white shadow-sm">
      
      <!-- Search by phone -->
      <div class="p-3 border-bottom sticky-top bg-white">
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          placeholder="🔍 Search by phone..."
          class="form-control rounded-pill"
        />

        <!-- search results -->
        <div
          v-if="searchResults.length"
          class="bg-white border mt-2 rounded shadow-sm overflow-auto"
          style="max-height: 250px;"
        >
          <div
            v-for="u in searchResults"
            :key="u.id"
            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
            @click="openUser(u)"
          >
            <div>
              <div class="fw-semibold">{{ u.display_name || u.profile_name || u.phone_number }}</div>
              <div class="text-muted small">{{ u.phone_number }}</div>
            </div>
            <span class="badge bg-primary">Chat</span>
          </div>
        </div>
      </div>

      <!-- Inbox -->
      <div class="flex-grow-1 overflow-auto">
        <div
          v-for="c in inbox"  
          :key="c.user_id"
          @click="selectConversation(c)"
          class="p-3 border-bottom cursor-pointer chat-preview"
          :class="selectedUserId === c.user_id ? 'bg-light fw-bold' : ''"
        >
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">{{ c.other_user.name|| c.other_user.phone_number }}</h6>
            <small class="text-muted" v-if="c.timestamp">
              {{ formatTime(c.timestamp) }}
            </small>
          </div>
          <p class="text-truncate small text-secondary mb-0">{{ c.last_message_preview }}</p>
        </div>
      </div>
    </div>

    <!-- RIGHT: Chat Window -->
    <div class="col-8 d-flex flex-column bg-white shadow-sm" v-if="selectedUserId">
      
      <!-- Header with Save Contact -->
      <div class="p-3 border-bottom d-flex justify-content-between align-items-center sticky-top bg-white">
        <div class="fw-semibold fs-5">
          {{ selectedDisplayName || selectedPhone }}
          <p class="text-muted small mb-0">{{ selectedPhone }}</p>
        </div>
        <div v-if="!hasSavedName">
          <button @click="promptSaveContact" class="btn btn-outline-primary btn-sm rounded-pill">
             {{ hasSavedName ? 'Update Contact' : 'Save Contact' }}
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div class="flex-grow-1 overflow-auto p-3 chat-messages" ref="messagesPane">
        <div v-for="m in messages" :key="m.id" class="mb-3">
          
          <!-- My message -->
          <div v-if="m.sender_id === userId" class="text-end">
            <span class="d-inline-block px-3 py-2 rounded-3 bg-primary text-white shadow-sm">
              {{ m.message_text }}
            </span>
            <div class="small text-muted mt-1">
              {{ formatTime(m.sent_at) }}
            </div>
          </div>

          <!-- Other user's message -->
          <div v-else class="text-start">
            <span class="d-inline-block px-3 py-2 rounded-3 bg-light border shadow-sm">
              {{ m.message_text }}
            </span>
            <div class="small text-muted mt-1">
              {{ formatTime(m.sent_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="p-3 border-top d-flex bg-light">
        <input
          v-model="newMessage"
          placeholder="Type a message..."
          class="form-control me-2 rounded-pill"
          @keyup.enter="sendMessage"
        />
        <button
          @click="sendMessage"
          class="btn btn-primary rounded-pill px-4"
          :disabled="!newMessage.trim()"
        >
          ➤
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div
      class="col-8 d-flex align-items-center justify-content-center text-muted fs-5"
      v-else
    >
      Select a conversation or search by phone to start chatting 💬
    </div>
  </div>
</template>

<script>
import debounce from 'lodash.debounce';
import { decodeToken } from '@/utils/auth';
import {io} from "socket.io-client";
export default {
  data() {
    return {
      // assume you store auth user id somewhere (or fetch from /me)
      userId: decodeToken(localStorage.getItem('token')).user_id,
      

      inbox: [],
      messages: [],
      selectedUserId: null,
      selectedDisplayName: '',
      selectedPhone: '',
      hasSavedName: false,

      newMessage: '',

      searchQuery: '',
      searchResults: [],
      socket : null,
    };
  },
  methods: {
    authHeaders() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` };
    },
    formatTime(ts) {
      try {
        return new Date(ts).toLocaleString(
          undefined,
          { dateStyle: 'short', timeStyle: 'short' },

        );
      } catch {
        return ts;
      }
    },

    async loadInbox() {
      const res = await fetch('/api/messages/inbox', { headers: this.authHeaders() });
      this.inbox = await res.json();
      console.log("Inbox:", this.inbox);
    },

    async selectConversation(conv) {
      this.selectedUserId = conv.other_user.id;
      this.selectedDisplayName = conv.other_user.name || '';
      this.selectedPhone = conv.other_user.phone_number || '';
      this.hasSavedName = Boolean(conv.other_user.name );
      await this.loadConversation(this.selectedUserId);
      this.$nextTick(this.scrollToBottom);
    },

    async loadConversation(otherId) {
      const res = await fetch(`/api/messages/conversation/${otherId}`, { headers: this.authHeaders() });
      this.messages = await res.json();

      // If opened from search, we might not have display name yet
      if (!this.selectedDisplayName) {
        // find from inbox after refresh
        const row = this.inbox.find(i => i.user_id === otherId);
        if (row) {
          this.selectedDisplayName = row.display_name || '';
          this.selectedPhone = row.phone || '';
          this.hasSavedName = Boolean(row.display_name && row.display_name !== row.phone);
        }
      }
    },

     async sendMessage() {
      const text = this.newMessage.trim();
      if (!text || !this.selectedUserId) return;

      // Instead of only fetch → emit to socket
      const res = await fetch('/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
        body: JSON.stringify({
          receiver_id: this.selectedUserId,
          message_text: text
        })
      });
      if (res.ok){
        this.newMessage = '';
      }

      
    },

    scrollToBottom() {
      const el = this.$refs.messagesPane;
      if (el) el.scrollTop = el.scrollHeight;
    },

    onSearchInput: debounce(async function () {
      if (!this.searchQuery.trim()) {
        this.searchResults = [];
        return;
      }
      const res = await fetch(`/api/get_users/${this.searchQuery}`, {
        headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}},
        
      );
      const data = await res.json();
      this.searchResults =  Array.isArray(data) ? data : [data];
      console.log(this.searchResults);
    }, 300),

    async openUser(u) {
      // clear search dropdown
      this.searchResults = [];
      this.searchQuery = '';

      this.selectedUserId = u.id;
      this.selectedDisplayName = u.display_name || u.profile_name || '';
      this.selectedPhone = u.phone || '';
      this.hasSavedName = Boolean(u.display_name && u.display_name !== u.phone);

      await this.loadConversation(this.selectedUserId);
      await this.loadInbox();
      this.$nextTick(this.scrollToBottom);
    },

    async promptSaveContact() {
      const name = prompt('Save contact as (custom name):', this.selectedDisplayName || this.selectedPhone);
      if (name === null) return; // cancelled
      const saved_name = name.trim();
      if (!saved_name) return;

      await fetch('/api/save_contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
        body: JSON.stringify({
          contact_user_id: this.selectedUserId,
          saved_name
        })
      });

      this.hasSavedName = true;
      this.selectedDisplayName = saved_name;

      // Refresh inbox so it uses saved name
      await this.loadInbox();
    }
  },
  async mounted() {
    await this.loadInbox();
    // Connect socket
    this.socket = io("/", {
      transports: ["websocket"],
    });

    // Auto-join my room when connected
    this.socket.on("connect", () => {
      this.socket.emit("join", { room: this.userId });
    });

    // Listen for new incoming messages
    this.socket.on("receive_message", (msg) => {
      // Only add if it belongs to the current chat
      if (msg.sender_id === this.selectedUserId || msg.receiver_id === this.selectedUserId) {
        this.messages.push(msg);
        this.$nextTick(this.scrollToBottom);
      }
      // refresh inbox preview
      this.loadInbox();
    });
  }
};
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
.chat-preview:hover { background-color: #f8f9fa; }
.chat-messages { background: #fdfdfd; }
</style>
