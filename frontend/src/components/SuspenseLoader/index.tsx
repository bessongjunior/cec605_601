import { useEffect, Fragment } from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import NProgress from 'nprogress';

export const SuspenseLoader = () => {
    useEffect(() => {
        NProgress.start();
        return () => {
          NProgress.done();
        };
      }, []);

  return (
    <Fragment>
    <Box
      sx={{
        position: 'fixed',
        left: 0,
        top: 0,
        width: '100%',
        height: '100%'
      }}
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <CircularProgress size={64} disableShrink thickness={3} />
    </Box>
    </Fragment>
  );
  
}


