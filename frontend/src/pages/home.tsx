import {FC, Fragment} from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { HomeHero } from '../components/home';
import { HomePopularCourse} from '../components/home';
import {HomeFeature} from '../components/home';
import {HomeTestimonial} from '../components/home';
import {HomeOurMentors} from '../components/home';
import {HomeNewsLetter} from '../components/home';
import './../assets/styles/globals.css';
import './../assets/styles/react-slick.css'
import 'slick-carousel/slick/slick-theme.css'
import theme from '../config/theme';
import { Footer } from '../components/footer';
import { Header } from '../components/header';

export const HomePage: FC = () => {

    return (
        <Fragment>
            <ThemeProvider theme={theme}>
            <CssBaseline />
            <Header />

            <HomeHero />
            <HomePopularCourse />
            <HomeFeature />
            <HomeTestimonial />
            <HomeOurMentors />
            <HomeNewsLetter />
            <Footer />
            </ThemeProvider>
        </Fragment>
        );
}
