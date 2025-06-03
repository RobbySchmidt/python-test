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
          label="create Task"
          @click="addTodo()"/>
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
        <span :class="{ 'line-through' :todo.completed }">
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
  import { ref, onMounted } from 'vue'

  const todos = ref([])
  const newTodo = ref('')
  const successMessage = ref('')
  const errorMessage = ref('')

  // Fetch Todos from API
  const fetchTodos = async () => {
    try {
      todos.value = await $fetch('http://localhost:8000/todos')
    } catch (error) {
      errorMessage.value = 'Failed to fetch todos.'
      console.error(error)
    }
  }

  // Add a new todo
  const addTodo = async () => {
    if (!newTodo.value.trim()) {
      errorMessage.value = 'Todo cannot be empty.'
      successMessage.value = ''
      return
    }

    const todo = {
      id: Date.now(),
      title: newTodo.value.trim(),
      completed: false
    }

    try {
      await $fetch('http://localhost:8000/todos', {
        method: 'POST',
        body: todo
      })
      successMessage.value = `New Task "${newTask.value}" has been successfully added`
      errorMessage.value = ''
      newTodo.value = ''
      fetchTodos()
      setTimeout(() => {
        successMessage.value = ''
      }, 3000);
    } catch (error) {
      errorMessage.value = 'Failed to create task.'
      successMessage.value = ''
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000);
      console.error(error)
    }
  }

// Delete a todo
  const deleteTodo = async (id) => {
    try {
      await $fetch(`http://localhost:8000/todos/${id}`, {
        method: 'DELETE'
      })
      successMessage.value = 'Task deleted successfully.'
      errorMessage.value = ''
      fetchTodos()
    } catch (error) {
      errorMessage.value = 'Failed to delete task.'
      successMessage.value = ''
      console.error(error)
    }
  }

  // Toggle task completion
  const checkTask = async (id) => {
    const todo = todos.value.find(t => t.id === id)
    if (!todo) return

    const updatedTodo = {
      ...todo,
      completed: !todo.completed
    }

    try {
      await $fetch(`http://localhost:8000/todos/${id}`, {
        method: 'PATCH',
        body: updatedTodo
      })
      fetchTodos()
    } catch (error) {
      errorMessage.value = 'Failed to update task.'
      console.error(error)
    }
  }

  onMounted(fetchTodos)
</script>
