import React, { useState, useRef, useEffect, useCallback } from 'react';
import { X, Check, RotateCw } from 'lucide-react';
import './ImageCropper.css';

const ImageCropper = ({ imageSrc, onCrop, onCancel, aspectRatio = 1 }) => {
  const [crop, setCrop] = useState({ x: 0, y: 0, width: 100, height: 100 });
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [currentImageSrc, setCurrentImageSrc] = useState(imageSrc);
  const containerRef = useRef(null);
  const imageRef = useRef(null);
  const cropAreaRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState(null);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });

  useEffect(() => {
    setCurrentImageSrc(imageSrc);
  }, [imageSrc]);

  useEffect(() => {
    if (currentImageSrc && imageRef.current) {
      const img = new Image();
      img.onload = () => {
        const containerWidth = 500;
        const containerHeight = 500;
        const imgAspect = img.width / img.height;
        const containerAspect = containerWidth / containerHeight;
        
        let displayWidth, displayHeight;
        if (imgAspect > containerAspect) {
          displayWidth = containerWidth;
          displayHeight = containerWidth / imgAspect;
        } else {
          displayHeight = containerHeight;
          displayWidth = containerHeight * imgAspect;
        }
        
        setImageSize({ width: displayWidth, height: displayHeight });
        setPosition({ x: (containerWidth - displayWidth) / 2, y: (containerHeight - displayHeight) / 2 });
        
        // Initialize crop area to center
        const cropSize = Math.min(displayWidth, displayHeight) * 0.8;
        setCrop({
          x: (containerWidth - cropSize) / 2,
          y: (containerHeight - cropSize) / 2,
          width: cropSize,
          height: cropSize
        });
      };
      img.src = currentImageSrc;
    }
  }, [currentImageSrc]);

  const handleMouseDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const target = e.target;
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) return;
    
    // Check if clicking on a resize handle
    if (target.classList.contains('crop-handle-nw')) {
      setIsResizing(true);
      setResizeHandle('nw');
      setResizeStart({
        x: e.clientX,
        y: e.clientY,
        width: crop.width,
        height: crop.height,
        left: crop.x,
        top: crop.y
      });
    } else if (target.classList.contains('crop-handle-ne')) {
      setIsResizing(true);
      setResizeHandle('ne');
      setResizeStart({
        x: e.clientX,
        y: e.clientY,
        width: crop.width,
        height: crop.height,
        left: crop.x,
        top: crop.y
      });
    } else if (target.classList.contains('crop-handle-sw')) {
      setIsResizing(true);
      setResizeHandle('sw');
      setResizeStart({
        x: e.clientX,
        y: e.clientY,
        width: crop.width,
        height: crop.height,
        left: crop.x,
        top: crop.y
      });
    } else if (target.classList.contains('crop-handle-se')) {
      setIsResizing(true);
      setResizeHandle('se');
      setResizeStart({
        x: e.clientX,
        y: e.clientY,
        width: crop.width,
        height: crop.height,
        left: crop.x,
        top: crop.y
      });
    } else if (target === cropAreaRef.current || cropAreaRef.current?.contains(target)) {
      // Dragging the crop area
      setIsDragging(true);
      setDragStart({
        x: e.clientX - containerRect.left - crop.x,
        y: e.clientY - containerRect.top - crop.y
      });
    }
  };

  const handleMouseMove = useCallback((e) => {
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) return;
    
    if (isResizing) {
      e.preventDefault();
      const deltaX = e.clientX - resizeStart.x;
      const deltaY = e.clientY - resizeStart.y;
      const containerWidth = 500;
      const containerHeight = 500;
      const minSize = 50; // Minimum crop size
      
      let newCrop = { ...crop };
      
      switch (resizeHandle) {
        case 'se': // Southeast - resize from bottom-right
          newCrop.width = Math.max(minSize, Math.min(resizeStart.width + deltaX, containerWidth - resizeStart.left));
          newCrop.height = Math.max(minSize, Math.min(resizeStart.height + deltaY, containerHeight - resizeStart.top));
          // Maintain aspect ratio (square)
          const size = Math.min(newCrop.width, newCrop.height);
          newCrop.width = size;
          newCrop.height = size;
          break;
          
        case 'sw': // Southwest - resize from bottom-left
          newCrop.width = Math.max(minSize, Math.min(resizeStart.width - deltaX, resizeStart.left + resizeStart.width));
          newCrop.height = Math.max(minSize, Math.min(resizeStart.height + deltaY, containerHeight - resizeStart.top));
          const sizeSW = Math.min(newCrop.width, newCrop.height);
          newCrop.width = sizeSW;
          newCrop.height = sizeSW;
          newCrop.x = resizeStart.left + resizeStart.width - sizeSW;
          break;
          
        case 'ne': // Northeast - resize from top-right
          newCrop.width = Math.max(minSize, Math.min(resizeStart.width + deltaX, containerWidth - resizeStart.left));
          newCrop.height = Math.max(minSize, Math.min(resizeStart.height - deltaY, resizeStart.top + resizeStart.height));
          const sizeNE = Math.min(newCrop.width, newCrop.height);
          newCrop.width = sizeNE;
          newCrop.height = sizeNE;
          newCrop.y = resizeStart.top + resizeStart.height - sizeNE;
          break;
          
        case 'nw': // Northwest - resize from top-left
          newCrop.width = Math.max(minSize, Math.min(resizeStart.width - deltaX, resizeStart.left + resizeStart.width));
          newCrop.height = Math.max(minSize, Math.min(resizeStart.height - deltaY, resizeStart.top + resizeStart.height));
          const sizeNW = Math.min(newCrop.width, newCrop.height);
          newCrop.width = sizeNW;
          newCrop.height = sizeNW;
          newCrop.x = resizeStart.left + resizeStart.width - sizeNW;
          newCrop.y = resizeStart.top + resizeStart.height - sizeNW;
          break;
        default:
          // No resize handle selected, do nothing
          break;
      }
      
      // Ensure crop stays within bounds
      newCrop.x = Math.max(0, Math.min(newCrop.x, containerWidth - newCrop.width));
      newCrop.y = Math.max(0, Math.min(newCrop.y, containerHeight - newCrop.height));
      
      setCrop(newCrop);
    } else if (isDragging) {
      e.preventDefault();
      const newX = e.clientX - containerRect.left - dragStart.x;
      const newY = e.clientY - containerRect.top - dragStart.y;
      
      const maxX = 500 - crop.width;
      const maxY = 500 - crop.height;
      
      setCrop(prevCrop => ({
        ...prevCrop,
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      }));
    }
  }, [isResizing, isDragging, resizeStart, resizeHandle, crop, dragStart]);

  const handleMouseUp = () => {
    setIsDragging(false);
    setIsResizing(false);
    setResizeHandle(null);
  };

  useEffect(() => {
    if (isDragging || isResizing) {
      const moveHandler = (e) => handleMouseMove(e);
      const upHandler = () => handleMouseUp();
      
      document.addEventListener('mousemove', moveHandler);
      document.addEventListener('mouseup', upHandler);
      return () => {
        document.removeEventListener('mousemove', moveHandler);
        document.removeEventListener('mouseup', upHandler);
      };
    }
  }, [isDragging, isResizing, handleMouseMove]);

  const handleCrop = () => {
    console.log('🖼️ Starting crop process...');
    console.log('Crop state:', { crop, imageSize, position, currentImageSrc: !!currentImageSrc });
    
    if (!currentImageSrc || imageSize.width === 0 || imageSize.height === 0) {
      console.error('❌ Cannot crop: missing image data', {
        hasSrc: !!currentImageSrc,
        imageSize
      });
      return;
    }

    const img = new Image();
    img.crossOrigin = 'anonymous';
    
    img.onload = () => {
      try {
        console.log('📐 Image loaded:', { 
          imgWidth: img.width, 
          imgHeight: img.height,
          displayWidth: imageSize.width,
          displayHeight: imageSize.height
        });
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Calculate the scale factor between displayed image and actual image
        const scaleX = img.width / imageSize.width;
        const scaleY = img.height / imageSize.height;
        
        console.log('📏 Scale factors:', { scaleX, scaleY });
        
        // Calculate crop coordinates relative to the displayed image position
        // Crop area is relative to container (0,0), but image might be offset
        const relativeCropX = crop.x - position.x;
        const relativeCropY = crop.y - position.y;
        
        console.log('📍 Relative crop position:', { relativeCropX, relativeCropY });
        
        // Convert to actual image coordinates
        const cropX = Math.max(0, relativeCropX * scaleX);
        const cropY = Math.max(0, relativeCropY * scaleY);
        const cropWidth = Math.min(crop.width * scaleX, img.width - cropX);
        const cropHeight = Math.min(crop.height * scaleY, img.height - cropY);
        
        console.log('✂️ Final crop coordinates:', { cropX, cropY, cropWidth, cropHeight });
        
        // Ensure valid dimensions
        if (cropWidth <= 0 || cropHeight <= 0) {
          console.error('❌ Invalid crop dimensions:', { cropWidth, cropHeight });
          return;
        }
        
        // Set canvas size to crop size
        canvas.width = cropWidth;
        canvas.height = cropHeight;
        
        // Draw the cropped portion
        ctx.drawImage(
          img,
          cropX, cropY, cropWidth, cropHeight,
          0, 0, cropWidth, cropHeight
        );
        
        console.log('✅ Canvas drawn, converting to blob...');
        
        // Convert to blob
        canvas.toBlob((blob) => {
          if (blob) {
            console.log('✅ Crop successful, blob size:', blob.size, 'bytes');
            onCrop(blob);
          } else {
            console.error('❌ Failed to create blob from canvas');
          }
        }, 'image/jpeg', 0.95);
      } catch (error) {
        console.error('❌ Error during crop:', error);
        console.error('Stack:', error.stack);
      }
    };
    
    img.onerror = (error) => {
      console.error('❌ Failed to load image for cropping:', error);
    };
    
    img.src = currentImageSrc;
  };

  const handleRotate = () => {
    // Simple rotation - just update the image source
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Rotate 90 degrees clockwise
      canvas.width = img.height;
      canvas.height = img.width;
      
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate(Math.PI / 2);
      ctx.drawImage(img, -img.width / 2, -img.height / 2);
      
      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const newSrc = reader.result;
            setCurrentImageSrc(newSrc);
            
            // Recalculate dimensions after rotation
            const newImg = new Image();
            newImg.onload = () => {
              const containerWidth = 500;
              const containerHeight = 500;
              const imgAspect = newImg.width / newImg.height;
              const containerAspect = containerWidth / containerHeight;
              
              let displayWidth, displayHeight;
              if (imgAspect > containerAspect) {
                displayWidth = containerWidth;
                displayHeight = containerWidth / imgAspect;
              } else {
                displayHeight = containerHeight;
                displayWidth = containerHeight * imgAspect;
              }
              
              setImageSize({ width: displayWidth, height: displayHeight });
              setPosition({ x: (containerWidth - displayWidth) / 2, y: (containerHeight - displayHeight) / 2 });
              
              const cropSize = Math.min(displayWidth, displayHeight) * 0.8;
              setCrop({
                x: (containerWidth - cropSize) / 2,
                y: (containerHeight - cropSize) / 2,
                width: cropSize,
                height: cropSize
              });
            };
            newImg.src = newSrc;
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.95);
    };
    img.src = currentImageSrc;
  };

  return (
    <div className="image-cropper-overlay" onClick={onCancel}>
      <div className="image-cropper-modal" onClick={(e) => e.stopPropagation()}>
        <div className="image-cropper-header">
          <h3>Crop Profile Photo</h3>
          <div className="image-cropper-actions">
            <button
              type="button"
              onClick={handleRotate}
              className="btn-rotate"
              title="Rotate"
            >
              <RotateCw size={20} />
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="btn-cancel"
            >
              <X size={20} />
            </button>
          </div>
        </div>
        
        <div className="image-cropper-content">
          <div className="image-cropper-container" ref={containerRef}>
            <img
              ref={imageRef}
              src={currentImageSrc}
              alt="Crop preview"
              style={{
                position: 'absolute',
                left: `${position.x}px`,
                top: `${position.y}px`,
                width: `${imageSize.width}px`,
                height: `${imageSize.height}px`,
                objectFit: 'contain'
              }}
            />
            <div
              ref={cropAreaRef}
              className="crop-area"
              onMouseDown={handleMouseDown}
              style={{
                left: `${crop.x}px`,
                top: `${crop.y}px`,
                width: `${crop.width}px`,
                height: `${crop.height}px`,
                cursor: isDragging ? 'grabbing' : 'grab',
                userSelect: 'none'
              }}
            >
              <div className="crop-handle crop-handle-nw"></div>
              <div className="crop-handle crop-handle-ne"></div>
              <div className="crop-handle crop-handle-sw"></div>
              <div className="crop-handle crop-handle-se"></div>
            </div>
          </div>
        </div>
        
        <div className="image-cropper-footer">
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleCrop}
            className="btn-primary"
          >
            <Check size={20} />
            Apply Crop
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageCropper;

