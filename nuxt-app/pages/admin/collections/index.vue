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
    <div v-if="collections && collections.length" class="mt-6 space-y-2">
      <div
        v-for="collection in collections"
        :key="collection.id"
        class="p-4 border rounded-md hover:bg-gray-50 cursor-pointer flex justify-between items-center"
      >
        <span
          @click="navigateTo(`/admin/collections/${collection.id}`)"
          class="text-lg font-medium flex-grow"
        >
          {{ collection.name }}
        </span>

        <button
          @click.stop="deleteCollection(collection.id)"
          class="text-red-600 hover:text-red-800 ml-4"
          aria-label="Delete collection"
        >
          Delete
        </button>
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
    const data = await $fetch('http://localhost:8000/collections')
    collections.value = data || []
  } catch (err) {
    console.error(err)
    errorMessage.value = 'Failed to load collections.'
    collections.value = []
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

const deleteCollection = async (id) => {
  try {
    await $fetch(`http://localhost:8000/collections/${id}`, {
      method: 'DELETE',
    })
    successMessage.value = 'Collection deleted.'
    fetchCollections()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch (err) {
    console.error(err)
    errorMessage.value = 'Failed to delete collection.'
    setTimeout(() => (errorMessage.value = ''), 3000)
  }
}

const navigateTo = (path) => {
  router.push(path)
}

onMounted(fetchCollections)
</script>
