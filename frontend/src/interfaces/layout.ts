// import { NextPage } from 'next'
// import { ReactElement, ReactNode } from 'react'

// export type NextPageWithLayout = NextPage & {
//   getLayout?: (page: ReactElement) => ReactNode
// }

import { ReactElement, ReactNode, FC } from 'react';

type PageWithLayout = FC & {
  getLayout?: (page: ReactElement) => ReactNode
};

// Usage
const Page: PageWithLayout = () => {
  return '';
};

// Page.getLayout = (page) => {
//   return {page};
// };

export default Page;
