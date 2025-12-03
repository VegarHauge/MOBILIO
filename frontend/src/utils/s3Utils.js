// src/utils/s3Utils.js


const S3_BUCKET_NAME = 'dat535gruppe7vmf';
const S3_REGION = 'eu-north-1';
const S3_BASE_URL = `https://${S3_BUCKET_NAME}.s3.${S3_REGION}.amazonaws.com`;
const IMAGE_PREFIX = 'images';
const HERO_PREFIX = 'public'; 

// Function takes image name; returns image url 
// Example: https://dat535gruppe7vmf.s3.eu-north-1.amazonaws.com/public/index_hero.png
export const getImageUrl = (imageName, isHero=false) => {
  if (!imageName) {
    console.error('Provide image name');
    return '';
  }
  const cleanImageName = imageName.startsWith('/') ? imageName.slice(1) : imageName;

  if (isHero) {
    return `${S3_BASE_URL}/${HERO_PREFIX}/${cleanImageName}`;
  }

  return `${S3_BASE_URL}/${IMAGE_PREFIX}/${cleanImageName}`;
};