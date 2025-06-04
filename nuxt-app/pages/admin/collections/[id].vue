<template>
  <div class="container mx-auto p-8 max-w-4xl">
    <h1 class="text-2xl font-bold mb-6">
      Manage Collection: <span class="text-blue-600">{{ collection?.name || 'Loading...' }}</span>
    </h1>

    <!-- Fields Section -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Fields</h2>

      <div class="flex gap-2 mb-4">
        <UInput v-model="newFieldName" placeholder="Field name" />
        <select v-model="newFieldType" class="border rounded px-2">
          <option value="string">String</option>
          <option value="boolean">Boolean</option>
          <option value="number">Number</option>
        </select>
        <UButton label="Add Field" @click="addField" />
      </div>

      <ul>
        <li v-for="field in fields" :key="field.id" class="py-1 border-b">
          {{ field.name }} ({{ field.type }})
        </li>
      </ul>
    </section>

    <!-- Records Section -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Records</h2>

      <table class="w-full table-auto border-collapse border border-gray-300 mb-4">
        <thead>
          <tr class="bg-gray-100">
            <th class="border border-gray-300 px-3 py-1">ID</th>
            <th
              v-for="field in fields"
              :key="field.id"
              class="border border-gray-300 px-3 py-1"
            >
              {{ field.name }}
            </th>
            <th class="border border-gray-300 px-3 py-1">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.id" class="hover:bg-gray-50">
            <td class="border border-gray-300 px-3 py-1 text-xs">{{ record.id }}</td>
            <td
              v-for="field in fields"
              :key="field.id"
              class="border border-gray-300 px-3 py-1"
            >
              <!-- Show boolean as checkbox -->
              <template v-if="field.type === 'boolean'">
                <input
                  type="checkbox"
                  :checked="record.data[field.name]"
                  @change="toggleBoolean(record, field.name)"
                />
              </template>
              <template v-else>
                {{ record.data[field.name] }}
              </template>
            </td>
            <td class="border border-gray-300 px-3 py-1">
              <button @click="deleteRecord(record.id)" class="text-red-600 hover:underline">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add New Record Form -->
      <div class="border p-4 rounded">
        <h3 class="text-lg font-semibold mb-3">Add New Record</h3>
        <form @submit.prevent="addRecord" class="space-y-4">
          <div
            v-for="field in fields"
            :key="field.id"
            class="flex flex-col"
          >
            <label :for="field.name" class="mb-1 font-medium">{{ field.name }}</label>
            <template v-if="field.type === 'boolean'">
              <input
                type="checkbox"
                :id="field.name"
                v-model="newRecordData[field.name]"
              />
            </template>
            <template v-else-if="field.type === 'number'">
              <input
                type="number"
                :id="field.name"
                v-model.number="newRecordData[field.name]"
                class="border rounded p-1"
                required
              />
            </template>
            <template v-else>
              <input
                type="text"
                :id="field.name"
                v-model="newRecordData[field.name]"
                class="border rounded p-1"
                required
              />
            </template>
          </div>

          <UButton label="Add Record" type="submit" />
        </form>
      </div>
    </section>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="text-green-500 mt-4">{{ successMessage }}</div>
    <div v-if="errorMessage" class="text-red-500 mt-4">{{ errorMessage }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collectionId = route.params.id

const collection = ref(null)
const fields = ref([])
const records = ref([])

const newFieldName = ref('')
const newFieldType = ref('string')

const newRecordData = ref({})

const successMessage = ref('')
const errorMessage = ref('')

// Fetch collection info
const fetchCollection = async () => {
  try {
    const res = await $fetch(`http://localhost:8000/collections`)
    collection.value = res.find(c => c.id === collectionId) || null
  } catch (e) {
    errorMessage.value = 'Failed to load collection info.'
  }
}

// Fetch fields
const fetchFields = async () => {
  try {
    fields.value = await $fetch(`http://localhost:8000/collections/${collectionId}/fields`)
    resetNewRecordData()
  } catch {
    errorMessage.value = 'Failed to load fields.'
  }
}

// Fetch records
const fetchRecords = async () => {
  try {
    records.value = await $fetch(`http://localhost:8000/collections/${collectionId}/records`)
  } catch {
    errorMessage.value = 'Failed to load records.'
  }
}

// Add field
const addField = async () => {
  const name = newFieldName.value.trim()
  if (!name) {
    errorMessage.value = 'Field name cannot be empty.'
    return
  }
  try {
    await $fetch(`http://localhost:8000/collections/${collectionId}/fields`, {
      method: 'POST',
      body: {
        name,
        type: newFieldType.value,
      },
    })
    successMessage.value = `Field "${name}" added.`
    newFieldName.value = ''
    newFieldType.value = 'string'
    errorMessage.value = ''
    fetchFields()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch {
    errorMessage.value = 'Failed to add field.'
  }
}

// Reset newRecordData based on fields
function resetNewRecordData() {
  newRecordData.value = {}
  fields.value.forEach(f => {
    if (f.type === 'boolean') {
      newRecordData.value[f.name] = false
    } else if (f.type === 'number') {
      newRecordData.value[f.name] = 0
    } else {
      newRecordData.value[f.name] = ''
    }
  })
}

// Add record
const addRecord = async () => {
  // Validate required fields
  for (const f of fields.value) {
    if (f.type !== 'boolean' && !newRecordData.value[f.name]) {
      errorMessage.value = `Field "${f.name}" cannot be empty.`
      return
    }
  }
  try {
    await $fetch(`http://localhost:8000/collections/${collectionId}/records`, {
      method: 'POST',
      body: {
        data: newRecordData.value,
      },
    })
    successMessage.value = 'Record added.'
    errorMessage.value = ''
    resetNewRecordData()
    fetchRecords()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch {
    errorMessage.value = 'Failed to add record.'
  }
}

// Delete record
const deleteRecord = async (id) => {
  try {
    await $fetch(`http://localhost:8000/records/${id}`, {
      method: 'DELETE',
    })
    successMessage.value = 'Record deleted.'
    errorMessage.value = ''
    fetchRecords()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch {
    errorMessage.value = 'Failed to delete record.'
  }
}

// Toggle boolean field in record inline
const toggleBoolean = async (record, fieldName) => {
  const updatedData = { ...record.data, [fieldName]: !record.data[fieldName] }
  try {
    await $fetch(`http://localhost:8000/records/${record.id}`, {
      method: 'PATCH',
      body: { data: updatedData },
    })
    fetchRecords()
  } catch {
    errorMessage.value = 'Failed to update record.'
  }
}

// Fetch data initially
onMounted(() => {
  fetchCollection()
  fetchFields()
  fetchRecords()
})
</script>
