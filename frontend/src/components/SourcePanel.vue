<template>
  <section class="sources">
    <h4>引用来源</h4>
    <article v-for="(source, index) in sources" :key="source.id" class="source-card">
      <header>
        <span class="source-index">[{{ index + 1 }}]</span>
        <strong>{{ source.title }}</strong>
        <span class="source-meta">{{ source.source }} · 块 #{{ source.chunk_index + 1 }}</span>
        <span class="score">相关度 {{ (source.score * 100).toFixed(1) }}%</span>
      </header>
      <p>{{ source.content }}</p>
    </article>
  </section>
</template>

<script setup>
defineProps({
  sources: { type: Array, required: true },
});
</script>
