<template>
  <article class="message-row" :class="role">
    <div class="avatar" :class="role" aria-hidden="true">
      {{ role === "user" ? "你" : "AI" }}
    </div>
    <div class="message-content">
      <div class="message-meta">{{ role === "user" ? "你" : "助手" }}</div>
      <div class="message-body">
        <MarkdownContent v-if="role === 'assistant'" :content="content" />
        <p v-else class="user-text">{{ content }}</p>
      </div>
      <SourcePanel v-if="role === 'assistant' && sources?.length" :sources="sources" />
    </div>
  </article>
</template>

<script setup>
import MarkdownContent from "./MarkdownContent.vue";
import SourcePanel from "./SourcePanel.vue";

defineProps({
  role: { type: String, required: true },
  content: { type: String, required: true },
  sources: { type: Array, default: () => [] },
});
</script>
