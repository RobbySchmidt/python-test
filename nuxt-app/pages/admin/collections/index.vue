<template>
  <div class="container mx-auto p-8">
    <h1 class="text-2xl font-bold mb-6">Collections</h1>

    <!-- Create New Collection -->
    <div class="flex gap-2 mb-4">
      <UInput v-model="newCollection" placeholder="New collection name" class="w-full" />
      <UButton @click="createCollection" label="Create" />
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="text-green-500">{{ successMessage }}</div>
    <div v-if="errorMessage" class="text-red-500">{{ errorMessage }}</div>

    <!-- List of Collections -->
    <div v-if="collections.length" class="mt-6 space-y-2">
      <div
        v-for="collection in collections"
        :key="collection.id"
        class="p-4 border rounded-md hover:bg-gray-50 cursor-pointer flex justify-between items-center"
        @click="navigateTo(`/admin/collections/${collection.id}`)"
      >
        <span class="text-lg font-medium">{{ collection.name }}</span>
        <UIcon name="i-lucide-arrow-right" />
      </div>
    </div>
    <div v-else class="text-gray-500 mt-4">No collections yet.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const collections = ref([])
const newCollection = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const router = useRouter()

const fetchCollections = async () => {
  try {
    collections.value = await $fetch('http://localhost:8000/collections')
  } catch (err) {
    console.error(err)
    errorMessage.value = 'Failed to load collections.'
  }
}

const createCollection = async () => {
  const name = newCollection.value.trim()
  if (!name) {
    errorMessage.value = 'Collection name cannot be empty.'
    return
  }

  try {
    await $fetch('http://localhost:8000/collections', {
      method: 'POST',
      body: { name },
    })
    successMessage.value = `Collection "${name}" created.`
    newCollection.value = ''
    fetchCollections()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch (err) {
    console.error(err)
    errorMessage.value = 'Failed to create collection.'
    setTimeout(() => (errorMessage.value = ''), 3000)
  }
}

const navigateTo = (path) => {
  router.push(path)
}

onMounted(fetchCollections)
</script>
