// import { Suspense, lazy } from 'react';
// import { Navigate } from 'react-router-dom';
// import { RouteObject } from 'react-router';
// import {SuspenseLoader }from './components/SuspenseLoader';
import {createBrowserRouter, RouterProvider } from 'react-router-dom'; 

import { HomePage } from './pages/home';

// import { HomePage } from './views/pages/homepage';  
// import { UserSignIn } from './views/auth/loginpage';
// import { UserSignUp } from './views/auth/registerpage';
// import { PasswordReset } from './views/auth/passwordresetpage';
// import { UserProfile } from './views/dashboard/Profile';
// import { UserSettings } from './views/dashboard/Setting';
// import { UserDashboard } from './views/dashboard/UserDashboard';
// import { UserReport } from './views/dashboard/Report';

// import { DashboardLayout } from './layouts/DashboardLayout';
// import { SignIn } from './pages/Auth/Signin';
// import { SignUp } from './pages/Auth/Signup';
// import { ResetPasscode } from './pages/Auth/ResetPassword';
// const Dashboard = lazy(() => import('./pages/dashboard'));
// const Profile = lazy(() => import('./pages/Profile'));
// const Users = lazy(() => import('./pages/User'));

// // const LazyPage = lazy(() => import('./LazyPage'));
// // const LazyPage = lazy(() => import('./LazyPage'));

//     // element=( 
//     //     <Suspense fallback={<div>Loading…</div>}>
//     //     <LazyPage />
//     //     </Suspense>
//     // )

const router = createBrowserRouter([
    {
        path: '/',
        element: <HomePage />
    },
//     {
//         path: '/user/login',
//         element: <UserSignIn />
//     },
//     {
//         path: '/user/register',
//         element: <UserSignUp />
//     },
//     {
//         path: '/user/reset-password',
//         element: <PasswordReset />
//     },
//     {
//         path: '/user/dashboard',
//         element: <UserDashboard />
//     },
//     {
//         path: '/user/profile',
//         element: <UserProfile />
//     },
//     {
//         path: '/user/settings',
//         element: <UserSettings />
//     },
//     {
//         path: '/user/report',
//         element: <UserReport />
//     },
//     // {
//     //     path: '/',
//     //     element: < />
//     // },
//     {
//         path: 'admin/signin',
//         element: <SignIn />,
//     },
//     {
//         path: 'admin/signup',
//         element: <SignUp />
//     },
//     {
//         path: 'admin/passcode-reset',
//         element: <ResetPasscode />
//     },
//     {
//         path: 'admin',
//         element: <DashboardLayout />,
//         children: [
//             {
//                 path: 'dashboard',
//                 element: ( 
//                     <Suspense fallback={<SuspenseLoader />}>
//                         <Dashboard />
//                     </Suspense>
//                 )
//             },
//             {
//                 path: 'users',
//                 element: (
//                     <Suspense fallback={<SuspenseLoader />}>
//                         <Users />
//                     </Suspense>
//                 )
//             },
//             {
//                 path: 'profile',
//                 element: (
//                     <Suspense fallback={<SuspenseLoader />}>
//                         <Profile />
//                     </Suspense>
//                 )
//             },
//         ]
//     }
]);

export function Routes() {
    return <RouterProvider router={router} />;
}



