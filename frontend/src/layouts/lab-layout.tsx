import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
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

interface LabLayoutProps {
  children: ReactNode
}

export function LabLayout({ children }: LabLayoutProps) {
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
                <BreadcrumbPage>Lab</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex-1 p-6">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  )
}