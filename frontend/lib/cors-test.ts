// Test CORS configuration
export const testCors = async () => {
  try {
    const response = await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/v1/auth/test', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      console.log('CORS test successful');
      return true;
    } else {
      console.error('CORS test failed with status:', response.status);
      return false;
    }
  } catch (error) {
    console.error('CORS test failed with error:', error);
    return false;
  }
};