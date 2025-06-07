import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getAllUsers, toggleUserAdmin } from '../services/api';
import PdfUpload from './PdfUpload';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box,
} from '@mui/material';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
}

const AdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const { user } = useAuth();

  const fetchUsers = async () => {
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleToggleAdmin = async (userId: number) => {
    try {
      await toggleUserAdmin(userId);
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error toggling admin status:', error);
    }
  };

  if (!user?.is_admin) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Access Denied: Admin privileges required
        </Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Admin Dashboard
        </Typography>
        <PdfUpload />
        <TableContainer component={Paper} sx={{ mt: 4 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Admin</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </TableCell>
                  <TableCell>
                    {user.is_admin ? 'Yes' : 'No'}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      color={user.is_admin ? 'error' : 'primary'}
                      onClick={() => handleToggleAdmin(user.id)}
                      disabled={user.id === user.id} // Disable for current user
                    >
                      {user.is_admin ? 'Remove Admin' : 'Make Admin'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
};

export default AdminDashboard; 