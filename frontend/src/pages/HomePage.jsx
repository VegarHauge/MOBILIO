import React from "react";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import FeatureRow from "../components/FeatureRow";
import HeroSection from "../components/HeroSection";
import { getImageUrl } from "../utils/s3Utils";

export default function HomePage() {
  const location = useLocation();

  useEffect(() => {
    if (location.state?.jumpToProducts) {
      window.scrollTo({
        top: window.innerHeight,
        behavior: "auto",
      });
    }
  }, [location]);

  return (
    <MainLayout hero={
      <HeroSection
        title="Velkommen"
        subtitle="Fremtidens elektronikk, levert i dag."
        buttonText="Produkter"
        buttonLink="/products"
        backgroundImage={getImageUrl("index_hero.png", true)}
      />
    } navColor="light">
      {/* Content below Hero */}
      <FeatureRow
        title="Mobiltelefoner"
        text="Utforsk våre Mobiltelefoner."
        image={getImageUrl("smartphones.png", true)}
        link="/products/Mobiltelefon"
      />
      <FeatureRow
        title="Hodetelefoner"
        text="Opplev krystalklar lyd."
        image={getImageUrl("headphones.png", true)}
        link="/products/headphones"
        reverse
      />
      <FeatureRow
        title="Tilbehør"
        text="Oppgrader stilen og funksjonen – med vårt tilbehør."
        image={getImageUrl("accessories.png", true)}
        link="/products/Smartklokke"
      />
    </MainLayout>
  );
}