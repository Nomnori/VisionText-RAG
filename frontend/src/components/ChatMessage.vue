<template>
  <article class="message" :class="role">
    <header class="message-header">
      <span class="badge">{{ role === "user" ? "你" : "助手" }}</span>
    </header>
    <p class="message-body">{{ content }}</p>
    <SourcePanel v-if="sources?.length" :sources="sources" />
  </article>
</template>

<script setup>
import SourcePanel from "./SourcePanel.vue";

defineProps({
  role: { type: String, required: true },
  content: { type: String, required: true },
  sources: { type: Array, default: () => [] },
});
</script>
