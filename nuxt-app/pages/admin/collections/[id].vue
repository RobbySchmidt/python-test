<template>
  <div class="container mx-auto p-8 max-w-4xl">
    <UButton @click="$router.push('/admin/collections')" class="group duration-300 ease-in-out cursor-pointer">
      <UIcon class="group-hover:-translate-x-1 duration-300 ease-in-out" name="i-lucide-arrow-left" />
      Back
    </UButton>

    <h1 class="text-2xl font-bold my-4">
      Manage Collection: <span class="text-blue-600">{{ collection?.name || 'Loading...' }}</span>
    </h1>

    <!-- Fields Section -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Fields</h2>

      <div class="flex gap-2 mb-4">
        <UInput v-model="newFieldName" placeholder="Field name" />
        <USelect v-model="newFieldType" :items="items" class="w-48" />
        <UButton label="Add Field" @click="addField" class="duration-300 ease-in-out cursor-pointer"/>
      </div>

      <ul>
        <li
          v-for="field in fields"
          :key="field.id"
          class="py-1 border-b flex justify-between items-center"
        >
          <span>{{ field.name }} ({{ field.type }})</span>
          <button @click="deleteField(field.id)" class="text-red-600 hover:underline text-sm">
            Delete
          </button>
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
              <template v-if="field.type.toLowerCase() === 'boolean'">
                <UCheckbox
                  :name="`record-${record.id}-${field.name}`"
                  :model-value="record.data[field.name]"
                  @update:model-value="(val) => toggleBoolean(record, field.name, val)"
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
          <div v-for="field in fields" :key="field.id" class="flex flex-col">
            <label :for="field.name" class="mb-1 font-medium">{{ field.name }}</label>
            <template v-if="field.type.toLowerCase() === 'boolean'">
              <UCheckbox
                :id="field.name"
                v-model="newRecordData[field.name]"
                :name="field.name"
              />
            </template>
            <template v-else-if="field.type.toLowerCase() === 'number'">
              <UInput
                type="number"
                :id="field.name"
                v-model.number="newRecordData[field.name]"
                required
              />
            </template>
            <template v-else>
              <UInput
                type="text"
                :id="field.name"
                v-model="newRecordData[field.name]"
                required
              />
            </template>
          </div>

          <UButton class="duration-300 ease-in-out cursor-pointer" label="Add Record" type="submit" />
        </form>
      </div>
    </section>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="text-green-500 mt-4">{{ successMessage }}</div>
    <div v-if="errorMessage" class="text-red-500 mt-4">{{ errorMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collectionId = route.params.id

const items = ref(['string', 'boolean', 'number'])
const newFieldType = ref('string')
const newFieldName = ref('')

const collection = ref(null)
const fields = ref([])
const records = ref([])

const newRecordData = ref<{ [key: string]: any }>({})

const successMessage = ref('')
const errorMessage = ref('')

const fetchCollection = async () => {
  try {
    const res = await $fetch(`http://localhost:8000/collections`)
    collection.value = res.find(c => c.id === collectionId) || null
  } catch {
    errorMessage.value = 'Failed to load collection info.'
  }
}

const fetchFields = async () => {
  try {
    fields.value = await $fetch(`http://localhost:8000/collections/${collectionId}/fields`)
    resetNewRecordData()
  } catch {
    errorMessage.value = 'Failed to load fields.'
  }
}

const fetchRecords = async () => {
  try {
    records.value = await $fetch(`http://localhost:8000/collections/${collectionId}/records`)
  } catch {
    errorMessage.value = 'Failed to load records.'
  }
}

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

const deleteField = async (fieldId: string) => {

  try {
    await $fetch(`http://localhost:8000/collections/${collectionId}/fields/${fieldId}`, {
      method: 'DELETE',
    })
    successMessage.value = 'Field deleted.'
    errorMessage.value = ''
    fetchFields()
    fetchRecords()
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch {
    errorMessage.value = 'Failed to delete field.'
  }
}

function resetNewRecordData() {
  newRecordData.value = {}
  fields.value.forEach(f => {
    const type = f.type.toLowerCase()
    if (type === 'boolean') {
      newRecordData.value[f.name] = false
    } else if (type === 'number') {
      newRecordData.value[f.name] = 0
    } else {
      newRecordData.value[f.name] = ''
    }
  })
}

const addRecord = async () => {
  for (const f of fields.value) {
    const type = f.type.toLowerCase()
    if (type !== 'boolean' && !newRecordData.value[f.name]) {
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

const deleteRecord = async (id: string) => {
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

const toggleBoolean = async (record: any, fieldName: string, newValue: boolean) => {
  const updatedData = { ...record.data, [fieldName]: newValue }
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

onMounted(() => {
  fetchCollection()
  fetchFields()
  fetchRecords()
})
</script>
