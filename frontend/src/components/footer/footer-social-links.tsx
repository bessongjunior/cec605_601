import  { FC } from 'react'
import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import CssBaseline from '@mui/material/CssBaseline';
import { SocialLink } from '../../interfaces/social-link'

export const socialLinks: SocialLink[] = [
  {
    name: ' ',
    link: '#',
    icon: 'assets/images/icons/instagram.svg',
  },
  {
    name: ' ',
    link: '#',
    icon: 'assets/images/icons/youtube.svg',
  },
  {
    name: ' ',
    link: '#',
    icon: 'assets/images/icons/twitter.svg',
  },
  {
    name: ' ',
    link: 'https://dribbble.com/shots/18114471-Coursespace-Online-Course-Landing-Page',
    icon: 'assets/images/icons/dribbble.svg',
  },
  {
    name: ' ',
    link: 'http://github.com/hiriski/coursespace-landing-page',
    icon: 'assets/images/icons/github.svg',
  },
]

interface SocialLinkItemProps {
  item: SocialLink
}

const SocialLinkItem: FC<SocialLinkItemProps> = ({ item }) => (
  <>
  <CssBaseline />
  <Box
    component="li"
    sx={{
      display: 'inline-block',
      color: 'primary.contrastText',
      mr: 0.5,
    }}
  >
    <Link
      target="_blank"
      sx={{
        lineHeight: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 36,
        height: 36,
        borderRadius: '50%',
        color: 'inherit',
        '&:hover': {
          backgroundColor: 'secondary.main',
        },
        '& img': {
          fill: 'currentColor',
          width: 22,
          height: 'auto',
        },
      }}
      href={item.link}
    >
      {/* eslint-disable-next-line */}
      <img src={item.icon} alt={item.name + 'icon'} />
    </Link>
  </Box>
  </>
)

// default
const SocialLinks: FC = () => {
  return (
    <>
    <CssBaseline />
    <Box sx={{ ml: -1 }}>
      <Box
        component="ul"
        sx={{
          m: 0,
          p: 0,
          lineHeight: 0,
          borderRadius: 3,
          listStyle: 'none',
        }}
      >
        {socialLinks.map((item) => {
          return <SocialLinkItem key={item.name} item={item} />
        })}
      </Box>
    </Box>
    </>
  )
}

export default SocialLinks
