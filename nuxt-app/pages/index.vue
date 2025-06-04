<template>
  <div class="container mx-auto py-12">
    <div class="space-y-4 lg:w-8/12 mx-auto">
      <div class="flex gap-2 items-center justify-between">
        <UInput 
          type="text"
          spellcheck="false"
          v-model="newTodo"
          class="w-full" />
        <UButton
          label="create Todo"
          :disabled="loading"
          @click="addTodo()" />
      </div>
      <div>
        <span v-if="successMessage" class="text-green-500">
          {{ successMessage }}
        </span>
        <span v-if="errorMessage" class="text-red-500">
          {{ errorMessage }}
        </span>
      </div>
      <div v-for="todo in todos" :key="todo.id" class="flex items-center justify-between">
        <span :class="{ 'line-through' : todo.completed }">
          {{ todo.title }}
        </span>
        <div class="flex gap-2">
          <span 
            @click="checkTask(todo.id)" 
            class="text-white border-2 rounded-full p-1 cursor-pointer w-6 h-6 flex items-center"
            :class="todo.completed ? 'bg-green-500 border-green-500' : 'bg-yellow-500 border-yellow-500'">
            <UIcon name="i-lucide-check" class="size-4" />
          </span>
          <span 
            @click="deleteTodo(todo.id)" 
            class="text-white bg-red-500 border-2 border-red-500 rounded-full p-1 cursor-pointer w-6 h-6 flex items-center">
            <UIcon name="i-lucide-x" class="size-4" />
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const COLLECTION_ID = '6a907db1-921f-4e07-a6e3-1201388a3bdd'  // your actual collection id
const API_BASE = `http://localhost:8000/collections/${COLLECTION_ID}`
const RECORDS_API = `${API_BASE}/records`

const todos = ref([])
const newTodo = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const loading = ref(false)

// Helper to show success or error messages with auto-clear
const showMessage = (type, text, duration = 3000) => {
  if (type === 'success') {
    successMessage.value = text
    errorMessage.value = ''
  } else {
    errorMessage.value = text
    successMessage.value = ''
  }
  setTimeout(() => {
    successMessage.value = ''
    errorMessage.value = ''
  }, duration)
}

// Fetch all todos (records) from backend and map them to flat todos
const fetchTodos = async () => {
  loading.value = true
  try {
    const records = await $fetch(RECORDS_API)
    todos.value = records.map(r => ({
      id: r.id,
      title: r.data.title,
      completed: r.data.completed
    }))
  } catch (error) {
    showMessage('error', 'Failed to fetch todos.')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Add a new todo via POST request
const addTodo = async () => {
  if (!newTodo.value.trim()) {
    showMessage('error', 'Todo cannot be empty.')
    return
  }

  const newRecord = {
    data: {
      title: newTodo.value.trim(),
      completed: false,
    }
  }

  loading.value = true
  try {
    await $fetch(RECORDS_API, { method: 'POST', body: newRecord })
    showMessage('success', `New Todo "${newTodo.value}" has been successfully added`)
    newTodo.value = ''
    await fetchTodos()
  } catch (error) {
    showMessage('error', 'Failed to create task.')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Delete a todo by record id
const deleteTodo = async (id) => {
  loading.value = true
  try {
    await $fetch(`http://localhost:8000/records/${id}`, { method: 'DELETE' })
    showMessage('success', 'Todo deleted successfully.')
    await fetchTodos()
  } catch (error) {
    showMessage('error', 'Failed to delete Todo.')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Toggle completion status of a todo by record id
const checkTask = async (id) => {
  const todo = todos.value.find(t => t.id === id)
  if (!todo) return

  const updatedRecord = {
    data: {
      title: todo.title,
      completed: !todo.completed
    }
  }

  loading.value = true
  try {
    await $fetch(`http://localhost:8000/records/${id}`, { method: 'PATCH', body: updatedRecord })
    await fetchTodos()
  } catch (error) {
    showMessage('error', 'Failed to update task.')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Clear error message when input changes
watch(newTodo, () => {
  errorMessage.value = ''
})

// Load todos on page mount
onMounted(fetchTodos)
</script>
