import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCard from '../ProductCard';

const mockToggleFavorite = jest.fn();
const mockAddToCart = jest.fn(() => ({ success: true }));

jest.mock('../../contexts/FavoritesContext', () => ({
  useFavorites: () => ({
    isFavorite: (id) => id === 'prod_fav',
    toggleFavorite: mockToggleFavorite,
  })
}));

jest.mock('../../contexts/CartContext', () => ({
  useCart: () => ({
    addToCart: mockAddToCart
  })
}));

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true
  })
}));

describe('ProductCard', () => {
  const product = {
    product_id: 'prod_001',
    name: '테스트 상품',
    brand: '테스트 브랜드',
    price: 59000,
    image_url: 'https://example.com/image.jpg'
  };

  it('renders basic product info', () => {
    render(<ProductCard product={product} onClick={() => {}} />);

    expect(screen.getByText('테스트 브랜드')).toBeInTheDocument();
    expect(screen.getByText('테스트 상품')).toBeInTheDocument();
    expect(screen.getByText(/59,000원/)).toBeInTheDocument();
  });

  it('calls addToCart when cart button is clicked', () => {
    render(<ProductCard product={product} onClick={() => {}} />);

    const cartButton = screen.getByLabelText('장바구니에 추가');
    fireEvent.click(cartButton);

    expect(mockAddToCart).toHaveBeenCalled();
  });

  it('toggles favorite when favorite button is clicked', () => {
    render(<ProductCard product={{ ...product, product_id: 'prod_fav' }} onClick={() => {}} />);

    const favButton = screen.getByLabelText('좋아요');
    fireEvent.click(favButton);

    expect(mockToggleFavorite).toHaveBeenCalledWith('prod_fav');
  });
});
