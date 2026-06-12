<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

interface Message {
  role: string
  content: string
}

const inputMessage = ref('')
const messages = ref<Message[]>([])
const loading = ref(false)
const threadId = ref<string | null>(null)
const scrollEl = ref<HTMLElement | null>(null)
const textareaEl = ref<HTMLTextAreaElement | null>(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollEl.value) {
      scrollEl.value.scrollTop = scrollEl.value.scrollHeight
    }
  })
}

const autoGrow = () => {
  nextTick(() => {
    if (textareaEl.value) {
      textareaEl.value.style.height = 'auto'
      textareaEl.value.style.height = Math.min(textareaEl.value.scrollHeight, 200) + 'px'
    }
  })
}

watch([messages, loading], scrollToBottom, { deep: true })
watch(inputMessage, autoGrow)

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  loading.value = true
  autoGrow()

  try {
    const payload: any = {
      messages: [{ role: 'user', content: userMessage }]
    }
    if (threadId.value) {
      payload.thread_id = threadId.value
    }

    const response = await axios.post('/api/v1/agent/chat', payload)

    if (response.data.thread_id) {
      threadId.value = response.data.thread_id
    }

    if (response.data.output && response.data.output.messages) {
      const msgs = response.data.output.messages
      const lastMsg = msgs[msgs.length - 1]
      if (lastMsg && lastMsg.role === 'assistant') {
        messages.value.push(lastMsg)
      } else {
        messages.value.push({ role: 'assistant', content: 'Empty response' })
      }
    } else if (response.data.output && response.data.output.error) {
      messages.value.push({ role: 'assistant', content: `Error: ${response.data.output.error}` })
    } else {
      messages.value.push({ role: 'assistant', content: 'Agent finished execution but did not return messages.' })
    }
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: 'Network Error: ' + error.message })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex h-screen w-full flex-col overflow-x-hidden bg-[#F7F5F0]">

    <!-- Top bar -->
    <header class="flex h-14 shrink-0 items-center justify-between px-6">
      <div class="flex items-center gap-2">
        <span class="font-serif text-[15px] text-[#3D3929]">Agent</span>
        <span v-if="threadId" class="font-mono text-[11px] text-[#A39E8E]">
          {{ threadId.slice(0, 8) }}
        </span>
      </div>
      <div class="flex items-center gap-1.5 rounded-full border border-[#E8E4DA] bg-white/60 px-3 py-1 text-[11px] text-[#8C8878]">
        <span class="h-1.5 w-1.5 rounded-full" :class="loading ? 'bg-[#D97757]' : 'bg-[#8FAE8B]'"></span>
        {{ loading ? 'Thinking' : 'Ready' }}
      </div>
    </header>

    <!-- Body -->
    <div ref="scrollEl" class="flex-1 overflow-y-auto">
      <div class="mx-auto flex min-h-full w-full max-w-[720px] flex-col px-6">

        <!-- Empty state -->
        <div v-if="messages.length === 0" class="flex flex-1 flex-col items-center justify-center pb-10 text-center">
          <p class="font-serif text-[32px] leading-tight text-[#3D3929]">
            <span class="mr-1 text-[#D97757]">✺</span>What can I help with?
          </p>
          <p class="mt-3 max-w-[380px] text-[14px] leading-relaxed text-[#A39E8E]">
            Ask a question to start a conversation with the agent.
          </p>
        </div>

        <!-- Conversation -->
        <div v-else class="flex flex-col gap-6 py-8">
          <div v-for="(msg, index) in messages" :key="index" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
            <div
              v-if="msg.role === 'user'"
              class="msg-content max-w-[75%] rounded-2xl bg-[#EDE9E0] px-4 py-2.5 text-[15px] leading-relaxed text-[#3D3929]"
              v-html="md.render(msg.content)"
            ></div>
            <div
              v-else
              class="msg-content w-full text-[15px] leading-relaxed text-[#3D3929]"
              v-html="md.render(msg.content)"
            ></div>
          </div>

          <!-- Loading indicator -->
          <div v-if="loading" class="flex items-center gap-1.5 py-1">
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-[#C9C3B4] [animation-delay:-0.3s]"></span>
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-[#C9C3B4] [animation-delay:-0.15s]"></span>
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-[#C9C3B4]"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Composer -->
    <div class="shrink-0 px-6 pb-6">
      <div class="mx-auto w-full max-w-[720px]">
        <div class="rounded-3xl border border-[#E8E4DA] bg-white shadow-sm shadow-black/[0.02]">
          <textarea
            ref="textareaEl"
            v-model="inputMessage"
            rows="1"
            placeholder="Message the agent..."
            :disabled="loading"
            @keydown.enter.exact.prevent="sendMessage"
            class="w-full resize-none bg-transparent px-5 pt-4 text-[15px] leading-relaxed text-[#3D3929] placeholder-[#B7B2A4] outline-none disabled:opacity-50"
            style="max-height: 200px"
          ></textarea>
          <div class="flex items-center justify-between px-3 pb-3 pt-1">
            <span class="px-2 text-[12px] text-[#C9C3B4]">Enter to send · Shift + Enter for newline</span>
            <button
              @click="sendMessage"
              :disabled="loading || !inputMessage.trim()"
              class="flex h-8 w-8 items-center justify-center rounded-full bg-[#3D3929] text-white transition-colors hover:bg-[#2A271C] disabled:cursor-not-allowed disabled:bg-[#E8E4DA] disabled:text-[#C9C3B4]"
            >
              <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4">
                <path fill-rule="evenodd" d="M10 17a.75.75 0 0 1-.75-.75V5.612L5.29 9.77a.75.75 0 0 1-1.08-1.04l5.25-5.5a.75.75 0 0 1 1.08 0l5.25 5.5a.75.75 0 1 1-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0 1 10 17Z" clip-rule="evenodd" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" class="h-4 w-4 animate-spin">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" stroke-opacity="0.25" />
                <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.msg-content {
  overflow-wrap: anywhere;
  word-break: break-word;
}
.msg-content :deep(p) {
  margin: 0;
}
.msg-content :deep(p + p) {
  margin-top: 0.65rem;
}
.msg-content :deep(ul),
.msg-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}
.msg-content :deep(li) {
  margin: 0.2rem 0;
}
.msg-content :deep(li::marker) {
  color: #C9C3B4;
}
.msg-content :deep(a) {
  color: #D97757;
  text-decoration: underline;
  text-decoration-color: rgba(217, 119, 87, 0.35);
  text-underline-offset: 2px;
}
.msg-content :deep(strong) {
  color: #2A271C;
  font-weight: 600;
}
.msg-content :deep(pre) {
  margin: 0.65rem 0;
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid #E8E4DA;
  background-color: #FBFAF7;
  padding: 0.85rem 1rem;
  font-size: 0.82rem;
  line-height: 1.6;
  color: #3D3929;
}
.msg-content :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.85em;
}
.msg-content :deep(p code) {
  border-radius: 0.3rem;
  background-color: #EDE9E0;
  color: #B6552F;
  padding: 0.15rem 0.4rem;
}
.msg-content :deep(blockquote) {
  margin: 0.65rem 0;
  border-left: 2px solid #E8E4DA;
  padding-left: 0.85rem;
  color: #8C8878;
}

.font-serif {
  font-family: 'Source Serif Pro', Georgia, 'Times New Roman', serif;
}
</style>