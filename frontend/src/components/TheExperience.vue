<script setup lang="ts">
import type { TresObject } from '@tresjs/core'
import { useLoop } from '@tresjs/core'
import { shallowRef } from 'vue'
import { Vector3 } from 'three'

const { onBeforeRender } = useLoop()

const boxRef = shallowRef<TresObject | null>(null)

onBeforeRender(({ elapsed }) => {
  if (boxRef.value) {
    boxRef.value.rotation.y = elapsed
    boxRef.value.rotation.z = elapsed
  }
})
</script>

<template>
  <TresPerspectiveCamera :position="new Vector3(5, 5, 5)" :look-at="new Vector3(0, 0, 0)" />
  <TresAmbientLight
    :intensity="0.5"
    color="white"
  />
  <TresMesh
    ref="boxRef"
    :position="new Vector3(0, 2, 0)"
  >
    <TresBoxGeometry :args="[1, 1, 1]" />
    <TresMeshNormalMaterial />
  </TresMesh>
  <TresDirectionalLight
    :position="new Vector3(0, 2, 4)"
    :intensity="1"
    cast-shadow
  />
  <TresAxesHelper />
  <TresGridHelper :args="[10, 10]" />
</template>