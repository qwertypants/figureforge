import type { Meta, StoryObj } from "@storybook/react";
import { within, userEvent } from "@storybook/testing-library";
import { expect } from "@storybook/jest";
import ImageCard from "./ImageCard";
import { Image } from "../types/types";
import useAuthStore from "../stores/authStore";
import useImageStore from "../stores/imageStore";

// Mock data
const mockImage: Image = {
  id: "1",
  url: "https://picsum.photos/400/600",
  thumbnail_url: "https://picsum.photos/200/300",
  user_id: "user123",
  prompt: "A figure drawing reference",
  parameters: {
    batch_size: 1,
    body_type: "athletic",
    pose_type: "standing",
    camera_angle: "eye_level",
    lighting: "studio",
    clothing: "athletic",
    background: "simple",
    ethnicity: "diverse",
    age_range: "adult",
    gender_presentation: "androgynous",
  },
  created_at: new Date().toISOString(),
  is_public: true,
  is_favorite: false,
};

const meta = {
  title: "Components/ImageCard",
  component: ImageCard,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div style={{ width: "300px" }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ImageCard>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic story - logged out user
export const Default: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().logout();
      return <Story />;
    },
  ],
};

// Logged in user - not favorited
export const LoggedInNotFavorited: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      useImageStore.getState().removeFromFavorites(mockImage.id);
      return <Story />;
    },
  ],
};

// Logged in user - favorited image
export const Favorited: Story = {
  args: {
    image: { ...mockImage, is_favorite: true },
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      useImageStore.getState().addToFavorites(mockImage.id);
      return <Story />;
    },
  ],
};

// User's own image - with delete action
export const OwnImageWithActions: Story = {
  args: {
    image: mockImage,
    showActions: true,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "user123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return <Story />;
    },
  ],
};

// Without thumbnail - fallback to main image
export const NoThumbnail: Story = {
  args: {
    image: { ...mockImage, thumbnail_url: undefined },
    showActions: false,
  },
};

// Broken image URL
export const BrokenImage: Story = {
  args: {
    image: {
      ...mockImage,
      url: "https://invalid-url.com/broken.jpg",
      thumbnail_url: "https://invalid-url.com/broken-thumb.jpg",
    },
    showActions: false,
  },
};

// Very long prompt text
export const LongPrompt: Story = {
  args: {
    image: {
      ...mockImage,
      prompt:
        "A highly detailed figure drawing reference with complex posing, dramatic lighting from multiple sources casting interesting shadows, wearing elaborate costume with flowing fabrics and intricate details, set against a detailed architectural background with perspective elements",
    },
    showActions: false,
  },
};

// Interactive story - hover to show actions
export const HoverInteraction: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return <Story />;
    },
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Initially, actions should not be visible
    const actionsContainer = canvas.getByRole("img").parentElement;
    const buttons = actionsContainer?.querySelectorAll("button");
    expect(buttons).toHaveLength(0);

    // Hover over the image to show actions
    const image = canvas.getByRole("img");
    await userEvent.hover(image);

    // The actions should now be visible
    const favoriteButton = await canvas.findByTitle(/Add to favorites/i);
    expect(favoriteButton).toBeInTheDocument();

    const reportButton = await canvas.findByTitle("Report image");
    expect(reportButton).toBeInTheDocument();
  },
};

// Favorite toggle interaction
export const FavoriteToggle: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      useImageStore.getState().removeFromFavorites(mockImage.id);
      return <Story />;
    },
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Hover to show actions
    const image = canvas.getByRole("img");
    await userEvent.hover(image);

    // Click favorite button
    const favoriteButton = await canvas.findByTitle(/Add to favorites/i);
    await userEvent.click(favoriteButton);

    // Button should now show as favorited
    const unfavoriteButton = await canvas.findByTitle(/Remove from favorites/i);
    expect(unfavoriteButton).toBeInTheDocument();
  },
};

// Report modal full flow
export const ReportModalFlow: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return <Story />;
    },
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Hover over the image
    const image = canvas.getByRole("img");
    await userEvent.hover(image);

    // Click the report button
    const reportButton = await canvas.findByTitle("Report image");
    await userEvent.click(reportButton);

    // The modal should appear
    const modal = await canvas.findByText("Report Image");
    expect(modal).toBeInTheDocument();

    // Select a reason
    const reasonSelect = canvas.getByRole("combobox");
    await userEvent.selectOptions(reasonSelect, "inappropriate");

    // Add details
    const detailsTextarea = canvas.getByRole("textbox");
    await userEvent.type(
      detailsTextarea,
      "This image contains inappropriate content",
    );

    // Test cancel button
    const cancelButton = canvas.getByText("Cancel");
    await userEvent.click(cancelButton);

    // Modal should be closed
    expect(canvas.queryByText("Report Image")).not.toBeInTheDocument();
  },
};

// Delete confirmation flow
export const DeleteConfirmation: Story = {
  args: {
    image: mockImage,
    showActions: true,
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "user123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return <Story />;
    },
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Hover to show actions
    const image = canvas.getByRole("img");
    await userEvent.hover(image);

    // Find delete button
    const deleteButton = await canvas.findByTitle("Delete image");
    expect(deleteButton).toBeInTheDocument();

    // Note: We can't actually test window.confirm in Storybook
    // but we verify the button exists and is clickable
  },
};

// Mobile view
export const Mobile: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  parameters: {
    viewport: {
      defaultViewport: "mobile1",
    },
  },
  decorators: [
    (Story) => {
      useAuthStore.getState().setUser({
        id: "123",
        email: "user@example.com",
        username: "artlover",
        role: "user",
        subscription: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return <Story />;
    },
  ],
};

// Tablet view
export const Tablet: Story = {
  args: {
    image: mockImage,
    showActions: false,
  },
  parameters: {
    viewport: {
      defaultViewport: "tablet",
    },
  },
};

// Loading state (simulated with a loading image)
export const Loading: Story = {
  args: {
    image: {
      ...mockImage,
      url: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect width="400" height="600" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3ELoading...%3C/text%3E%3C/svg%3E',
      thumbnail_url: undefined,
    },
    showActions: false,
  },
};

// Error state - image failed to load
export const ErrorState: Story = {
  args: {
    image: {
      ...mockImage,
      url: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect width="400" height="600" fill="%23fee"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23c33"%3EFailed to load%3C/text%3E%3C/svg%3E',
      thumbnail_url: undefined,
    },
    showActions: false,
  },
};

// Grid context - multiple cards
export const GridContext: Story = {
  decorators: [
    (Story) => (
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "1rem",
          width: "900px",
        }}
      >
        <Story />
        <ImageCard image={{ ...mockImage, id: "2" }} />
        <ImageCard image={{ ...mockImage, id: "3", is_favorite: true }} />
      </div>
    ),
  ],
  args: {
    image: mockImage,
    showActions: false,
  },
};
