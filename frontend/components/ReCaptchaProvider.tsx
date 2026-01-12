"use client";

import { GoogleReCaptchaProvider } from "react-google-recaptcha-v3";

interface ReCaptchaProviderProps {
  children: React.ReactNode;
}

export default function ReCaptchaProvider({ children }: ReCaptchaProviderProps) {
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || "";
  
  if (!siteKey) {
    console.warn("NEXT_PUBLIC_RECAPTCHA_SITE_KEY is not set. reCAPTCHA will not work.");
    return (
      <GoogleReCaptchaProvider
        reCaptchaKey=""
        language="en"
      >
        {children}
      </GoogleReCaptchaProvider>
    );
  }

  return (
    <GoogleReCaptchaProvider
      reCaptchaKey={siteKey}
      language="en"
    >
      {children}
    </GoogleReCaptchaProvider>
  );
}

