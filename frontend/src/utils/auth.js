import {jwtDecode}from 'jwt-decode';
import { useUserStore } from '@/store/userStore';

export function getToken() {
  return localStorage.getItem('token');
}

export function decodeToken() {
  const token = getToken();
  if (!token) return null;
  try {
    return jwtDecode(token);
  } catch (e) {
    console.error('Invalid token', e);
    return null;
  }
}

export function logoutUser() {
  const store = useUserStore();
  store.logout();
}

// utils/auth.js
export function isAuthenticated() {
  const user = decodeToken();
  if (!user) return false;
  if(!user.role) {
    console.error('User role is not defined in token');
    return false;
  
  }
  return user?.role ?? 'null';
}

