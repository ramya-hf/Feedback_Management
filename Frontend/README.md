# Feedback Management Frontend

A modern React TypeScript application for managing feedback, boards, and user interactions.

## 🚀 Features

- **Authentication System**: JWT-based login/register with role-based access control
- **Protected Routes**: Secure routing with role-based permissions
- **Modern UI**: Built with Tailwind CSS and Lucide React icons
- **Form Validation**: React Hook Form with Yup validation
- **Type Safety**: Full TypeScript implementation
- **API Integration**: Axios-based API service layer with automatic token refresh
- **Responsive Design**: Mobile-first responsive layout

## 🛠 Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router DOM** for routing
- **React Hook Form** for form management
- **Yup** for validation
- **Axios** for API communication
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **clsx & tailwind-merge** for conditional styling

## 📁 Project Structure

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── Dashboard.tsx
│   └── ProtectedRoute.tsx
├── contexts/
│   └── AuthContext.tsx
├── services/
│   └── api.ts
├── types/
│   └── index.ts
├── utils/
│   └── index.ts
├── App.tsx
├── main.tsx
└── index.css
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

## 🔐 Authentication

The application uses JWT tokens for authentication:

- **Access Token**: Short-lived token for API requests
- **Refresh Token**: Long-lived token for getting new access tokens
- **Automatic Refresh**: Tokens are automatically refreshed when they expire
- **Role-based Access**: Different permissions for admin, moderator, and contributor roles

### User Roles

- **Admin**: Full system access and management
- **Moderator**: Can manage feedback and moderate content
- **Contributor**: Can submit feedback and participate in discussions

## 🎨 UI Components

### Form Components
- **LoginForm**: Email/password authentication
- **RegisterForm**: User registration with comprehensive validation

### Layout Components
- **Dashboard**: Main application interface with stats and quick actions
- **ProtectedRoute**: Route wrapper for authentication and authorization

### Utility Components
- **Loading Spinners**: For async operations
- **Error Messages**: For form validation and API errors
- **Status Badges**: For feedback status, priority, and categories

## 🔧 Configuration

### API Configuration
The API base URL is configured in `src/services/api.ts`:
```typescript
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  // ...
});
```

### Tailwind Configuration
Custom colors and utilities are defined in `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#eff6ff',
        // ... more shades
        900: '#1e3a8a',
      },
    },
  },
}
```

## 📱 Responsive Design

The application is built with a mobile-first approach:

- **Mobile**: Single column layout with collapsible navigation
- **Tablet**: Two-column grid layouts
- **Desktop**: Full multi-column layouts with sidebar navigation

## 🔄 State Management

- **React Context**: For global authentication state
- **Local State**: For component-specific state
- **Form State**: Managed by React Hook Form

## 🧪 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- **TypeScript**: Strict type checking enabled
- **ESLint**: Code linting with React and TypeScript rules
- **Prettier**: Code formatting (if configured)

## 🔗 API Integration

The application integrates with the Django backend API:

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/me/` - Current user info

### Boards Endpoints
- `GET /api/boards/` - List boards
- `POST /api/boards/` - Create board
- `GET /api/boards/{id}/` - Get board details
- `PUT /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board

### Feedback Endpoints
- `GET /api/feedback/` - List feedback
- `POST /api/feedback/` - Create feedback
- `GET /api/feedback/{id}/` - Get feedback details
- `PUT /api/feedback/{id}/` - Update feedback
- `DELETE /api/feedback/{id}/` - Delete feedback

### Comments Endpoints
- `GET /api/comments/` - List comments
- `POST /api/comments/` - Create comment
- `GET /api/comments/{id}/` - Get comment details
- `PUT /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment

## 🚀 Deployment

### Environment Variables
Create a `.env` file for environment-specific configuration:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Feedback Management
```

### Build Process
1. Run `npm run build`
2. The built files will be in the `dist/` directory
3. Deploy the contents of `dist/` to your web server

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub
