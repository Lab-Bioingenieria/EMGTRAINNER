import type { ReactNode } from 'react'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '../components/ui/sidebar'
import { AppSidebar } from '../components/app-sidebar'
import { Separator } from '../components/ui/separator'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../components/ui/breadcrumb'
import { Link } from 'react-router-dom'

interface ConfigLayoutProps {
  children: ReactNode
}

export function ConfigLayout({ children }: ConfigLayoutProps) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="md:ml-[16rem] md:w-[calc(100%-16rem)] transition-[margin-left,width] duration-200 ease-linear group-data-[state=collapsed]/sidebar-wrapper:md:ml-[3rem] group-data-[state=collapsed]/sidebar-wrapper:md:w-[calc(100%-3rem)]">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-border px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link to="/">Home</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Device Configuration</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex flex-col h-full">
          <div className="border-b border-border bg-background px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-foreground">Device Configuration</h1>
                <p className="text-sm text-muted-foreground mt-1">Manage and configure connected devices</p>
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-auto bg-background">{children}</div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

