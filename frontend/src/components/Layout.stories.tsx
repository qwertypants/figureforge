import type { Meta, StoryObj } from "@storybook/react";
import { within, userEvent } from "@storybook/testing-library";
import { expect } from "@storybook/jest";
import { BrowserRouter } from "react-router-dom";
import Layout from "./Layout";
import { AuthProvider } from "../contexts/AuthContext";
import useAuthStore from "../stores/authStore";
import { User } from "../types/types";

// Mock user data
const mockUser: User = {
  id: "123",
  email: "user@example.com",
  username: "artlover",
  role: "user",
  subscription: {
    plan: "pro",
    status: "active",
    quota_limit: 300,
    quota_remaining: 250,
    current_period_start: new Date().toISOString(),
    current_period_end: new Date(
      Date.now() + 30 * 24 * 60 * 60 * 1000,
    ).toISOString(),
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const meta = {
  title: "Components/Layout",
  component: Layout,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <BrowserRouter>
        <AuthProvider>
          <Story />
        </AuthProvider>
      </BrowserRouter>
    ),
  ],
} satisfies Meta<typeof Layout>;

export default meta;
type Story = StoryObj<typeof meta>;

// Default (logged out) state
export const LoggedOut: Story = {
  decorators: [
    (Story) => {
      // Reset auth state
      useAuthStore.getState().logout();
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Welcome to FigureForge</h1>
        <p>This is the logged out view of the layout.</p>
      </div>
    </Layout>
  ),
};

// Logged in with username
export const LoggedInWithUsername: Story = {
  decorators: [
    (Story) => {
      // Set authenticated state
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <p>Welcome back, {mockUser.username}!</p>
      </div>
    </Layout>
  ),
};

// Logged in without username (email only)
export const LoggedInEmailOnly: Story = {
  decorators: [
    (Story) => {
      // Set authenticated state without username
      useAuthStore.getState().setUser({
        ...mockUser,
        username: undefined,
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <p>Welcome back! Your email is displayed in the navigation.</p>
      </div>
    </Layout>
  ),
};

// Admin user
export const AdminUser: Story = {
  decorators: [
    (Story) => {
      // Set admin user
      useAuthStore.getState().setUser({ ...mockUser, role: "admin" });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
        <p>Admin controls and moderation tools would appear here.</p>
      </div>
    </Layout>
  ),
};

// No subscription (free user)
export const FreeUser: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        subscription: undefined,
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Free Account</h1>
        <p>Upgrade to access image generation features.</p>
      </div>
    </Layout>
  ),
};

// Expired subscription
export const ExpiredSubscription: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        subscription: {
          ...mockUser.subscription!,
          status: "inactive",
          current_period_end: new Date(
            Date.now() - 7 * 24 * 60 * 60 * 1000,
          ).toISOString(),
        },
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Subscription Expired</h1>
        <p>Your subscription expired 7 days ago. Please renew to continue.</p>
      </div>
    </Layout>
  ),
};

// Hobby subscription - low quota
export const HobbySubscriptionLowQuota: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        subscription: {
          ...mockUser.subscription!,
          plan: "hobby",
          quota_limit: 50,
          quota_remaining: 5,
        },
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Hobby Plan</h1>
        <p className="text-orange-600">
          Warning: You only have 5 images remaining this month!
        </p>
      </div>
    </Layout>
  ),
};

// Pro subscription - normal usage
export const ProSubscription: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Pro Plan</h1>
        <p>
          You have {mockUser.subscription!.quota_remaining} images remaining.
        </p>
      </div>
    </Layout>
  ),
};

// Studio subscription - high quota
export const StudioSubscription: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        subscription: {
          ...mockUser.subscription!,
          plan: "studio",
          quota_limit: 2000,
          quota_remaining: 1850,
        },
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Studio Plan</h1>
        <p>You have 1,850 images remaining this month.</p>
      </div>
    </Layout>
  ),
};

// Quota exhausted
export const QuotaExhausted: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        subscription: {
          ...mockUser.subscription!,
          quota_remaining: 0,
        },
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Quota Exhausted</h1>
        <p className="text-red-600">
          You've used all your images for this month. Upgrade or wait for
          renewal.
        </p>
      </div>
    </Layout>
  ),
};

// Mobile view - logged out
export const MobileLoggedOut: Story = {
  parameters: {
    viewport: {
      defaultViewport: "mobile1",
    },
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().logout();
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-4">
        <h1 className="text-xl font-bold mb-4">Mobile View</h1>
        <p>The navigation should be responsive and show mobile menu.</p>
      </div>
    </Layout>
  ),
};

// Mobile view - logged in
export const MobileLoggedIn: Story = {
  parameters: {
    viewport: {
      defaultViewport: "mobile1",
    },
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-4">
        <h1 className="text-xl font-bold mb-4">Mobile Dashboard</h1>
        <p>Authenticated mobile experience.</p>
      </div>
    </Layout>
  ),
};

// Tablet view
export const Tablet: Story = {
  parameters: {
    viewport: {
      defaultViewport: "tablet",
    },
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-6">
        <h1 className="text-xl font-bold mb-4">Tablet View</h1>
        <p>Medium-sized screen layout.</p>
      </div>
    </Layout>
  ),
};

// With very long username
export const LongUsername: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        ...mockUser,
        username: "verylongusernamethatmightcauselayoutissues",
      });
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Long Username Test</h1>
        <p>Testing how the layout handles very long usernames.</p>
      </div>
    </Layout>
  ),
};

// With long content to show scrolling
export const WithLongContent: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Long Content Page</h1>
        {Array.from({ length: 20 }, (_, i) => (
          <p key={i} className="mb-4">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
            ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat.
          </p>
        ))}
      </div>
    </Layout>
  ),
};

// Active navigation state
export const ActiveNavigation: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Active Navigation</h1>
        <p>
          The current page link should be highlighted with an underline border.
        </p>
      </div>
    </Layout>
  ),
};

// Navigation hover states
export const NavigationHover: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Navigation Hover Test</h1>
        <p>Hover over navigation links to see the underline effect.</p>
      </div>
    </Layout>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Find and hover over gallery link
    const galleryLink = canvas.getByText("Gallery");
    await userEvent.hover(galleryLink);

    // Find and hover over generate link
    const generateLink = canvas.getByText("Generate");
    await userEvent.hover(generateLink);
  },
};

// Logout interaction
export const LogoutInteraction: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Logout Test</h1>
        <p>Click the logout button to test the logout flow.</p>
      </div>
    </Layout>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Find logout button
    const logoutButton = canvas.getByText("Logout");
    expect(logoutButton).toBeInTheDocument();

    // Verify it's clickable
    expect(logoutButton).toBeEnabled();
  },
};

// Empty content
export const EmptyContent: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => <Layout>{/* No content */}</Layout>,
};

// Error state content
export const ErrorContent: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h1 className="text-2xl font-bold text-red-800 mb-2">
            Error Loading Page
          </h1>
          <p className="text-red-600">
            Something went wrong. Please try again later.
          </p>
        </div>
      </div>
    </Layout>
  ),
};

// Loading state content
export const LoadingContent: Story = {
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser(mockUser);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    </Layout>
  ),
};
