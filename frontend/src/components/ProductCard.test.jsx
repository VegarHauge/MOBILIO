import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ProductCard from "./ProductCard";
import { getImageUrl } from "../utils/s3Utils";

describe("ProductCard", () => {
  const product = {
    id: 123,
    name: "Test Product",
    description: "This is a test product",
    price: 199.99,
    image: "test.jpg",
  };

  test("renders product name, description, and price", () => {
    render(
      <MemoryRouter>
        <ProductCard product={product} />
      </MemoryRouter>
    );

    expect(screen.getByText("Test Product")).toBeInTheDocument();
    expect(screen.getByText("This is a test product")).toBeInTheDocument();
    expect(screen.getByText("NOK 199.99")).toBeInTheDocument();
  });

  test("renders correct link to product page", () => {
    render(
      <MemoryRouter>
        <ProductCard product={product} />
      </MemoryRouter>
    );

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/product/123");
  });

  test("renders image using real getImageUrl", () => {
    render(
      <MemoryRouter>
        <ProductCard product={product} />
      </MemoryRouter>
    );

    const image = screen.getByRole("img");

    const expectedUrl = getImageUrl("test.jpg");

    expect(image).toHaveAttribute("src", expectedUrl);
    expect(image).toHaveAttribute("alt", "Test Product");
  });
});
