import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Home,
  Briefcase,
  FileText,
  MessageCircle,
  Calendar,
  User,
  Users,
  ClipboardList,
  Settings,
  LogOut,
  Menu,
  GraduationCap,
  Building2,
  UserCheck,
  Shield
} from "lucide-react";

const Layout = ({ children, title = "" }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getRoleColor = (role) => {
    const colors = {
      student: "bg-blue-100 text-blue-800",
      recruiter: "bg-green-100 text-green-800",
      faculty: "bg-purple-100 text-purple-800",
      admin: "bg-red-100 text-red-800",
    };
    return colors[role] || "bg-gray-100 text-gray-800";
  };

  const getRoleIcon = (role) => {
    const icons = {
      student: GraduationCap,
      recruiter: Building2,
      faculty: UserCheck,
      admin: Shield,
    };
    const Icon = icons[role] || User;
    return <Icon className="h-4 w-4" />;
  };

  const getNavigationItems = () => {
    const baseItems = [
      { name: "Dashboard", href: "/dashboard", icon: Home },
      { name: "Jobs", href: "/jobs", icon: Briefcase },
      { name: "Profile", href: "/profile", icon: User },
      { name: "Career Chat", href: "/career-chat", icon: MessageCircle },
    ];

    const roleSpecificItems = {
      student: [
        { name: "My Applications", href: "/applications", icon: FileText },
        { name: "Interviews", href: "/interviews", icon: Calendar },
        { name: "Assessments", href: "/assessments", icon: ClipboardList },
      ],
      recruiter: [
        { name: "Post Job", href: "/recruiter/post-job", icon: Briefcase },
        { name: "Applications", href: "/recruiter/applications", icon: FileText },
        { name: "Schedule Interviews", href: "/interviews", icon: Calendar },
      ],
      faculty: [
        { name: "Student Management", href: "/faculty/students", icon: Users },
        { name: "Create Assessment", href: "/faculty/assessments", icon: ClipboardList },
        { name: "Assessment Results", href: "/faculty/results", icon: FileText },
      ],
      admin: [
        { name: "User Management", href: "/admin/users", icon: Users },
        { name: "System Settings", href: "/admin/settings", icon: Settings },
        { name: "Reports", href: "/admin/reports", icon: FileText },
      ],
    };

    return [...baseItems, ...(roleSpecificItems[user?.role] || [])];
  };

  const navigationItems = getNavigationItems();

  const NavItem = ({ item, mobile = false }) => {
    const isActive = location.pathname === item.href;
    const Icon = item.icon;

    return (
      <Link
        to={item.href}
        onClick={() => mobile && setSidebarOpen(false)}
        className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          isActive
            ? "bg-blue-100 text-blue-700"
            : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
        }`}
      >
        <Icon className="h-4 w-4 mr-3" />
        {item.name}
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Mobile Menu */}
            <div className="flex items-center">
              <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="lg:hidden">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-64 p-0">
                  <div className="flex flex-col h-full">
                    <div className="p-6 border-b">
                      <h1 className="text-xl font-bold text-gray-900">
                        Placement AI
                      </h1>
                    </div>
                    <nav className="flex-1 px-4 py-6 space-y-1">
                      {navigationItems.map((item) => (
                        <NavItem key={item.name} item={item} mobile={true} />
                      ))}
                    </nav>
                  </div>
                </SheetContent>
              </Sheet>

              <div className="flex items-center ml-4 lg:ml-0">
                <h1 className="text-xl font-bold text-gray-900">Placement AI</h1>
                {title && (
                  <>
                    <span className="text-gray-400 mx-2">/</span>
                    <span className="text-gray-600">{title}</span>
                  </>
                )}
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <Badge className={getRoleColor(user?.role)}>
                <div className="flex items-center space-x-1">
                  {getRoleIcon(user?.role)}
                  <span className="capitalize">{user?.role}</span>
                </div>
              </Badge>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user?.full_name}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="flex items-center">
                      <User className="mr-2 h-4 w-4" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:pt-16">
          <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
            <nav className="flex-1 px-4 py-6 space-y-1">
              {navigationItems.map((item) => (
                <NavItem key={item.name} item={item} />
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:pl-64">
          <div className="py-6 px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;