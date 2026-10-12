import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState('en');
  const [translations, setTranslations] = useState({});

  useEffect(() => {
    api.getTranslations()
      .then(res => setTranslations(res))
      .catch(err => console.error("Could not load translations:", err));
  }, []);

  const t = (key) => {
    if (translations[lang] && translations[lang][key]) {
      return translations[lang][key];
    }
    if (translations['en'] && translations['en'][key]) {
      return translations['en'][key];
    }
    return key;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
