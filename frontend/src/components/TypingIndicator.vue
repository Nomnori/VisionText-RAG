<template>
  <div class="typing-row">
    <div class="avatar assistant">AI</div>
    <div class="typing-content">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
      <span class="typing-text">正在检索并生成回答...</span>
    </div>
  </div>
</template>

<style scoped>
.typing-row {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 8px 0;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  flex-shrink: 0;
}

.avatar.assistant {
  background: #10b981;
  color: #fff;
}

.typing-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #9ca3af;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.typing-text {
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
