<script setup lang="ts">
/** 星级评分组件 1-5 星 */
const props = defineProps<{ modelValue: number; readonly?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const stars = [1, 2, 3, 4, 5]

function setStar(n: number) {
  if (!props.readonly) emit('update:modelValue', n)
}
</script>

<template>
  <span class="inline-flex gap-0.5">
    <button
      v-for="n in stars"
      :key="n"
      type="button"
      :disabled="readonly"
      @click="setStar(n)"
      :class="['star p-0.5 text-sm', { active: n <= modelValue, 'cursor-pointer hover:scale-110': !readonly }]"
    >
      ★
    </button>
  </span>
</template>
