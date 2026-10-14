<script setup lang="ts">
import { useNav } from '@slidev/client'
const { currentLayout, currentPage, total } = useNav()
</script>

<template>
  <footer v-if="currentLayout !== 'cover' && currentLayout !== 'end'" class="deck-footer">
    <span>Hamza Saidi &nbsp;·&nbsp; PFE Master D3SI &nbsp;·&nbsp; FSA Béni Mellal &nbsp;·&nbsp; 2025-2026</span>
    <span class="deck-page">{{ currentPage }} / {{ total }}</span>
  </footer>
</template>
