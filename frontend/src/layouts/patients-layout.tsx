import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AppSidebar } from '../components/app-sidebar'
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '../components/ui/sidebar'
import { Separator } from '../components/ui/separator'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../components/ui/breadcrumb'

interface PatientsLayoutProps {
  children: ReactNode
}

export function PatientsLayout({ children }: PatientsLayoutProps) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="md:ml-[16rem] md:w-[calc(100%-16rem)] transition-[margin-left,width] duration-200 ease-linear group-data-[state=collapsed]/sidebar-wrapper:md:ml-[3rem] group-data-[state=collapsed]/sidebar-wrapper:md:w-[calc(100%-3rem)]">
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink asChild>
                    <Link to="/">ProControl</Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Patients</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

