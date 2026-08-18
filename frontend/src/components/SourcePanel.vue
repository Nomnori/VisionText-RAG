<template>
  <section class="sources-wrap">
    <button type="button" class="sources-toggle" @click="expanded = !expanded">
      <span class="sources-icon">📎</span>
      <span>引用来源 ({{ sources.length }})</span>
      <span class="chevron" :class="{ open: expanded }">›</span>
    </button>

    <Transition name="sources-expand">
      <div v-show="expanded" class="sources-panel">
        <article v-for="(source, index) in sources" :key="source.id" class="source-card">
          <button type="button" class="source-header" @click="toggleSource(index)">
            <span class="source-index">[{{ index + 1 }}]</span>
            <span class="type-badge" :class="source.content_type">{{ typeLabel(source) }}</span>
            <span class="source-title">{{ source.title }}</span>
            <span class="source-score">{{ (source.score * 100).toFixed(0) }}%</span>
            <span class="chevron small" :class="{ open: openSources[index] }">›</span>
          </button>
          <div v-show="openSources[index]" class="source-body">
            <div class="source-meta">
              <span class="file-badge" :class="source.file_type">{{ fileLabel(source.file_type) }}</span>
              <span>{{ source.source }}</span>
              <span v-if="source.page_number">· 第 {{ source.page_number }} 页</span>
              <span>· 块 #{{ source.chunk_index + 1 }}</span>
            </div>
            <p>{{ source.content }}</p>
          </div>
        </article>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";

defineProps({
  sources: { type: Array, required: true },
});

const expanded = ref(false);
const openSources = reactive({});

function toggleSource(index) {
  openSources[index] = !openSources[index];
}

function typeLabel(source) {
  return source.modality_label || source.content_type || "文本";
}

function fileLabel(fileType) {
  if (fileType === "pdf") return "PDF";
  if (fileType === "markdown") return "MD";
  return fileType?.toUpperCase() || "FILE";
}
</script>

<style scoped>
.sources-wrap {
  margin-top: 12px;
}

.sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f9fafb;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.sources-toggle:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.sources-icon {
  font-size: 0.9rem;
}

.chevron {
  display: inline-block;
  transform: rotate(90deg);
  transition: transform 0.2s;
  color: #9ca3af;
  font-size: 1.1rem;
  line-height: 1;
}

.chevron.open {
  transform: rotate(-90deg);
}

.chevron.small {
  margin-left: auto;
  font-size: 1rem;
}

.sources-panel {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #fafafa;
}

.source-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
  font: inherit;
}

.source-header:hover {
  background: #f3f4f6;
}

.source-index {
  color: #2563eb;
  font-weight: 600;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.type-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 999px;
  flex-shrink: 0;
}

.type-badge.text,
.type-badge.markdown {
  background: #dbeafe;
  color: #1d4ed8;
}

.type-badge.table {
  background: #fef3c7;
  color: #b45309;
}

.type-badge.image {
  background: #ede9fe;
  color: #6d28d9;
}

.source-title {
  flex: 1;
  font-weight: 500;
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-score {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

.source-body {
  padding: 0 12px 12px;
  border-top: 1px solid #e5e7eb;
}

.source-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #6b7280;
  margin: 8px 0;
}

.file-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.file-badge.pdf {
  background: #fee2e2;
  color: #b91c1c;
}

.file-badge.markdown {
  background: #dcfce7;
  color: #15803d;
}

.source-body p {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: #4b5563;
  white-space: pre-wrap;
}

.sources-expand-enter-active,
.sources-expand-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.sources-expand-enter-from,
.sources-expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
