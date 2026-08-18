<script setup>
import { computed } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import hljs from "highlight.js";
import "highlight.js/styles/github.min.css";

const props = defineProps({
  content: { type: String, required: true },
});

marked.setOptions({
  breaks: true,
  gfm: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

const renderedHtml = computed(() => {
  const raw = marked.parse(props.content || "", { async: false });
  return DOMPurify.sanitize(raw, {
    ADD_ATTR: ["target", "rel"],
  });
});
</script>

<template>
  <div class="markdown-body" v-html="renderedHtml" />
</template>
