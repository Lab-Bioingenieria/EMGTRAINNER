import type { Component } from 'vue'
import { Brain, Users, Stethoscope, Hand } from 'lucide-vue-next'

export interface CardHomeProps {
    title: string
    subtitle: string
    description: string
    to: string
}

export interface HomeInterfaceItem extends CardHomeProps {
    icon: Component
}

export const interfaces: HomeInterfaceItem[] = [
    {
        title: "AI Model Console",
        description:
            "Dashboard técnico para análisis y mejora del modelo de IA. Visualización de métricas, confusion matrix y gestión de datasets.",
        to: "/ai-console",
        icon: Brain,
        subtitle: "Investigadores / Ingenieros",
    },
    {
        title: "Sesión Doctor",
        description:
            "Panel avanzado con gráficos de señales sEMG, predicción en tiempo real e indicadores de fatiga y consistencia.",
        to: "/doctor",
        icon: Stethoscope,
        subtitle: "Médicos / Fisioterapeutas",
    },
    {
        title: "Sesión Paciente",
        description: "Interfaz simplificada para uso autónomo y tele-rehabilitación con feedback visual inmediato.",
        to: "/patient",
        icon: Hand,
        subtitle: "Pacientes",
    },
    {
        title: "Panel de Pacientes",
        description: "Vista general de todos los pacientes con historial de sesiones y gráficos de evolución longitudinal.",
        to: "/dashboard",
        icon: Users,
        subtitle: "Administradores / Clínicos",
    },
]
