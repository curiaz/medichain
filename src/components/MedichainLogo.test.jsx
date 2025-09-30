import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MedichainLogo from './MedichainLogo';

describe('MedichainLogo Component', () => {
  describe('Default Rendering', () => {
    it('renders SVG logo by default', () => {
      render(<MedichainLogo />);
      
      // Check for the medical cross symbol in SVG mode
      const crossSymbol = screen.getByText('+');
      expect(crossSymbol).toBeInTheDocument();
      
      // Should not render PNG image by default
      expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });

    it('applies default size of 40px', () => {
      render(<MedichainLogo />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: '40px',
        height: '40px',
      });
    });

    it('does not show text by default', () => {
      render(<MedichainLogo />);
      
      expect(screen.queryByText('MEDICHAIN')).not.toBeInTheDocument();
    });
  });

  describe('PNG Logo Mode', () => {
    it('renders PNG image when usePng is true', () => {
      render(<MedichainLogo usePng={true} />);
      
      const logoImage = screen.getByRole('img', { name: /medichain logo/i });
      expect(logoImage).toBeInTheDocument();
      expect(logoImage).toHaveAttribute('src');
      
      // Should not render SVG elements in PNG mode
      expect(screen.queryByText('+')).not.toBeInTheDocument();
    });

    it('applies correct size to PNG image', () => {
      const testSize = 60;
      render(<MedichainLogo size={testSize} usePng={true} />);
      
      const logoImage = screen.getByRole('img', { name: /medichain logo/i });
      expect(logoImage).toHaveStyle({
        width: `${testSize}px`,
        height: `${testSize}px`,
        objectFit: 'contain',
      });
    });

    it('has proper alt text for accessibility', () => {
      render(<MedichainLogo usePng={true} />);
      
      const logoImage = screen.getByRole('img', { name: /medichain logo/i });
      expect(logoImage).toHaveAttribute('alt', 'MediChain Logo');
    });
  });

  describe('SVG Logo Mode', () => {
    it('renders SVG logo with medical cross', () => {
      render(<MedichainLogo usePng={false} />);
      
      const crossSymbol = screen.getByText('+');
      expect(crossSymbol).toBeInTheDocument();
    });

    it('applies gradient background to SVG logo', () => {
      render(<MedichainLogo />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        background: 'linear-gradient(135deg, #4dd0e1, #2196f3)',
        borderRadius: '50%',
      });
    });

    it('applies correct size to SVG logo', () => {
      const testSize = 80;
      render(<MedichainLogo size={testSize} />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: `${testSize}px`,
        height: `${testSize}px`,
      });
    });

    it('scales medical cross based on container size', () => {
      const testSize = 100;
      render(<MedichainLogo size={testSize} />);
      
      const crossSymbol = screen.getByText('+');
      expect(crossSymbol).toHaveStyle({
        fontSize: `${testSize * 0.6}px`,
      });
    });
  });

  describe('Size Variations', () => {
    it.each([
      [20, '20px'],
      [40, '40px'],
      [60, '60px'],
      [100, '100px'],
    ])('renders with size %i correctly', (size, expectedSize) => {
      render(<MedichainLogo size={size} />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: expectedSize,
        height: expectedSize,
      });
    });

    it('handles string size values', () => {
      render(<MedichainLogo size="50" />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: '50px',
        height: '50px',
      });
    });
  });

  describe('Text Display', () => {
    it('shows MEDICHAIN text when showText is true', () => {
      render(<MedichainLogo showText={true} />);
      
      const medichainText = screen.getByText('MEDICHAIN');
      expect(medichainText).toBeInTheDocument();
    });

    it('applies correct text styling', () => {
      render(<MedichainLogo showText={true} />);
      
      const medichainText = screen.getByText('MEDICHAIN');
      expect(medichainText).toHaveStyle({
        fontWeight: '700',
        letterSpacing: '1px',
        background: 'linear-gradient(135deg, #2196f3, #00bcd4)',
      });
    });

    it('applies different text sizes', () => {
      const textSizes = {
        sm: '16px',
        md: '20px',
        lg: '24px',
        xl: '28px'
      };

      Object.entries(textSizes).forEach(([size, expectedFontSize]) => {
        const { unmount } = render(<MedichainLogo showText={true} textSize={size} />);
        
        const medichainText = screen.getByText('MEDICHAIN');
        expect(medichainText).toHaveStyle({
          fontSize: expectedFontSize,
        });
        
        unmount();
      });
    });

    it('defaults to medium text size when not specified', () => {
      render(<MedichainLogo showText={true} />);
      
      const medichainText = screen.getByText('MEDICHAIN');
      expect(medichainText).toHaveStyle({
        fontSize: '20px', // md size
      });
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const customClass = 'custom-logo-class';
      render(<MedichainLogo className={customClass} />);
      
      const logoContainer = screen.getByText('+').closest('.medichain-logo-container');
      expect(logoContainer).toHaveClass(customClass);
    });

    it('maintains base className alongside custom className', () => {
      const customClass = 'custom-logo-class';
      render(<MedichainLogo className={customClass} />);
      
      const logoContainer = screen.getByText('+').closest('.medichain-logo-container');
      expect(logoContainer).toHaveClass('medichain-logo-container');
      expect(logoContainer).toHaveClass(customClass);
    });

    it('applies container flex styles', () => {
      render(<MedichainLogo />);
      
      const logoContainer = screen.getByText('+').closest('.medichain-logo-container');
      expect(logoContainer).toHaveStyle({
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      });
    });
  });

  describe('Animation and Visual Effects', () => {
    it('includes shimmer animation styles in SVG mode', () => {
      render(<MedichainLogo />);
      
      // Check if the keyframes are defined in the DOM
      const styleElement = document.querySelector('style');
      expect(styleElement).toBeInTheDocument();
      expect(styleElement.textContent).toContain('@keyframes logoShimmer');
    });

    it('applies box shadow to SVG logo', () => {
      render(<MedichainLogo />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        boxShadow: '0 4px 15px rgba(77, 208, 225, 0.3)',
      });
    });

    it('has overflow hidden for shimmer effect', () => {
      render(<MedichainLogo />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        overflow: 'hidden',
        position: 'relative',
      });
    });
  });

  describe('Component Props Validation', () => {
    it('handles undefined props gracefully', () => {
      expect(() => render(<MedichainLogo />)).not.toThrow();
    });

    it('handles null size prop', () => {
      expect(() => render(<MedichainLogo size={null} />)).not.toThrow();
    });

    it('handles boolean props correctly', () => {
      expect(() => render(<MedichainLogo showText={false} usePng={false} />)).not.toThrow();
    });

    it('handles empty className', () => {
      expect(() => render(<MedichainLogo className="" />)).not.toThrow();
    });
  });

  describe('Combined Props Scenarios', () => {
    it('renders PNG logo with text', () => {
      render(<MedichainLogo usePng={true} showText={true} size={50} />);
      
      const logoImage = screen.getByRole('img', { name: /medichain logo/i });
      const medichainText = screen.getByText('MEDICHAIN');
      
      expect(logoImage).toBeInTheDocument();
      expect(medichainText).toBeInTheDocument();
      expect(logoImage).toHaveStyle({
        width: '50px',
        height: '50px',
      });
    });

    it('renders SVG logo with text and custom class', () => {
      render(
        <MedichainLogo 
          usePng={false} 
          showText={true} 
          size={60} 
          textSize="lg" 
          className="header-logo" 
        />
      );
      
      const crossSymbol = screen.getByText('+');
      const medichainText = screen.getByText('MEDICHAIN');
      const container = screen.getByText('+').closest('.medichain-logo-container');
      
      expect(crossSymbol).toBeInTheDocument();
      expect(medichainText).toBeInTheDocument();
      expect(container).toHaveClass('header-logo');
      expect(medichainText).toHaveStyle({
        fontSize: '24px', // lg size
      });
    });

    it('renders large PNG logo with XL text', () => {
      render(
        <MedichainLogo 
          usePng={true} 
          showText={true} 
          size={120} 
          textSize="xl" 
        />
      );
      
      const logoImage = screen.getByRole('img', { name: /medichain logo/i });
      const medichainText = screen.getByText('MEDICHAIN');
      
      expect(logoImage).toHaveStyle({
        width: '120px',
        height: '120px',
      });
      expect(medichainText).toHaveStyle({
        fontSize: '28px', // xl size
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles zero size gracefully', () => {
      render(<MedichainLogo size={0} />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: '0px',
        height: '0px',
      });
    });

    it('handles very large size values', () => {
      const largeSize = 500;
      render(<MedichainLogo size={largeSize} />);
      
      const logoContainer = screen.getByText('+').parentElement;
      expect(logoContainer).toHaveStyle({
        width: `${largeSize}px`,
        height: `${largeSize}px`,
      });
    });

    it('handles invalid textSize gracefully', () => {
      render(<MedichainLogo showText={true} textSize="invalid" />);
      
      // Should not crash and fall back to default behavior
      const medichainText = screen.getByText('MEDICHAIN');
      expect(medichainText).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('provides proper alt text for PNG logo', () => {
      render(<MedichainLogo usePng={true} />);
      
      const logoImage = screen.getByRole('img');
      expect(logoImage).toHaveAttribute('alt', 'MediChain Logo');
    });

    it('does not have accessibility issues with SVG logo', () => {
      render(<MedichainLogo usePng={false} />);
      
      const crossSymbol = screen.getByText('+');
      expect(crossSymbol).toBeInTheDocument();
      // SVG logo should not have role="img" but should be accessible via text content
    });

    it('maintains proper contrast with gradient backgrounds', () => {
      render(<MedichainLogo showText={true} />);
      
      const medichainText = screen.getByText('MEDICHAIN');
      // The gradient text should have proper styling for visibility
      expect(medichainText).toHaveStyle({
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      });
    });
  });
});