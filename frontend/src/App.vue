<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>VisionText-RAG</h1>
        <p>本地 LLM + ChromaDB 知识库问答</p>
      </div>

      <section class="status-card">
        <h2>系统状态</h2>
        <ul>
          <li><span>LLM</span><strong class="truncate">{{ shortModel(health?.llm_model) }}</strong></li>
          <li><span>Embedding</span><strong class="truncate">{{ shortModel(health?.embedding_model) }}</strong></li>
          <li><span>VLM</span><strong class="truncate">{{ shortModel(health?.vlm_model) }}</strong></li>
          <li><span>GPU</span><strong>{{ health?.gpu_name || (health?.cuda_available ? "可用" : "不可用") }}</strong></li>
          <li><span>知识库</span><strong>MD {{ health?.md_files ?? 0 }} / PDF {{ health?.pdf_files ?? 0 }}</strong></li>
          <li><span>已索引块</span><strong>{{ health?.indexed_chunks ?? 0 }}</strong></li>
        </ul>
      </section>

      <section class="files-card">
        <div class="card-header">
          <h2>知识库文件</h2>
          <button class="ghost" :disabled="loadingIngest" @click="handleIngest">
            {{ loadingIngest ? "索引中..." : "重建索引" }}
          </button>
        </div>
        <p v-if="!knowledgeFiles.length" class="empty">将 .md / .pdf 文件放入 knowledge/ 目录</p>
        <ul v-else>
          <li v-for="file in knowledgeFiles" :key="file.path">
            <span class="file-type" :class="file.file_type">{{ file.file_type === 'pdf' ? 'PDF' : 'MD' }}</span>
            <span class="file-path">{{ file.path }}</span>
            <small>{{ formatSize(file.size_bytes) }}</small>
          </li>
        </ul>
      </section>
    </aside>

    <main class="chat-area">
      <section ref="messagesRef" class="messages">
        <div v-if="!messages.length" class="welcome">
          <h2>开始提问</h2>
          <p>回答会附带引用来源，便于核对知识库原文。</p>
        </div>
        <ChatMessage
          v-for="(message, index) in messages"
          :key="index"
          :role="message.role"
          :content="message.content"
          :sources="message.sources"
        />
        <TypingIndicator v-if="loadingChat" />
      </section>

      <form class="composer" @submit.prevent="handleSubmit">
        <textarea
          v-model="question"
          rows="3"
          placeholder="输入你的问题，例如：项目支持哪些文档格式？"
          :disabled="loadingChat"
        />
        <div class="composer-actions">
          <label>
            Top-K
            <input v-model.number="topK" type="number" min="1" max="10" />
          </label>
          <button type="submit" :disabled="loadingChat || !question.trim()">发送</button>
        </div>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </main>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from "vue";
import ChatMessage from "./components/ChatMessage.vue";
import TypingIndicator from "./components/TypingIndicator.vue";
import {
  fetchHealth,
  fetchKnowledgeFiles,
  ingestKnowledge,
  sendChat,
} from "./api/client.js";

const health = ref(null);
const knowledgeFiles = ref([]);
const messages = ref([]);
const question = ref("");
const topK = ref(4);
const loadingChat = ref(false);
const loadingIngest = ref(false);
const error = ref("");
const messagesRef = ref(null);

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function shortModel(path) {
  if (!path) return "-";
  const name = path.split(/[/\\]/).pop();
  return name.length > 22 ? `${name.slice(0, 20)}…` : name;
}

async function scrollToBottom() {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
}

async function refreshStatus() {
  const [healthData, files] = await Promise.all([fetchHealth(), fetchKnowledgeFiles()]);
  health.value = healthData;
  knowledgeFiles.value = files;
}

async function handleIngest() {
  loadingIngest.value = true;
  error.value = "";
  try {
    const result = await ingestKnowledge();
    await refreshStatus();
    messages.value.push({
      role: "assistant",
      content: result.message,
      sources: [],
    });
    await scrollToBottom();
  } catch (err) {
    error.value = err.message;
  } finally {
    loadingIngest.value = false;
  }
}

async function handleSubmit() {
  const text = question.value.trim();
  if (!text || loadingChat.value) return;

  messages.value.push({ role: "user", content: text, sources: [] });
  question.value = "";
  loadingChat.value = true;
  error.value = "";
  await scrollToBottom();

  try {
    const result = await sendChat(text, topK.value);
    messages.value.push({
      role: "assistant",
      content: result.answer,
      sources: result.sources,
    });
    await refreshStatus();
  } catch (err) {
    error.value = err.message;
  } finally {
    loadingChat.value = false;
    await scrollToBottom();
  }
}

onMounted(async () => {
  try {
    await refreshStatus();
  } catch (err) {
    error.value = `无法连接后端 API：${err.message}`;
  }
});
</script>
