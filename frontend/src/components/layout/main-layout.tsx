import { FC, ReactNode } from 'react'
import Box from '@mui/material/Box'
import { Footer } from '../footer'
import { Header } from '../header'

interface Props {
  children: ReactNode
}

const MainLayout: FC<Props> = ({ children }) => {
  return (
    <Box component="main">
      <Header />
      {children}
      <Footer />
    </Box>
  )
}

export default MainLayout
