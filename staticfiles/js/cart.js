document.addEventListener("DOMContentLoaded", function () {
    // Toggle cart sidebar
    document.getElementById("toggle-cart").addEventListener("click", function () {
        document.getElementById("cart-sidebar").classList.toggle("show");
        fetchCartData();  // ✅ Fetch latest cart data when opening sidebar
    });

    document.getElementById("close-cart").addEventListener("click", function () {
        document.getElementById("cart-sidebar").classList.remove("show");
    });

    // ✅ Add to Cart Functionality
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productId = this.dataset.productId;
            const addonCheckboxes = document.querySelectorAll(".addon-checkbox:checked");
            let selectedAddons = [];
            addonCheckboxes.forEach(checkbox => {
                selectedAddons.push(checkbox.dataset.addonId);
            });
            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    addons: selectedAddons
                })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error("Network response was not ok");
            })
            .then(data => {
                if (data.success) {
                    document.getElementById("cart-count").innerText = data.cart_count;
                    updateSidebarCart(data.cart_items, data.cart_total);
                } else {
                    console.error("Error adding to cart:", data.error);
                }
            })
            .catch(error => {
                console.error("There was a problem with the fetch operation:", error);
            });
        });
    });

    // Function to fetch cart summary on page load
    function fetchCartData() {
        fetch(`/cart/summary/`)
        .then(response => response.json())
        .then(data => {
            updateSidebarCart(data.cart_items, data.cart_total);
            document.getElementById("cart-count").innerText = data.cart_total_items; // ✅ Fix: Use correct total
        });
    }

    // ✅ Function to Update Sidebar Cart
    function updateSidebarCart(items, total) {
        const cartSidebarBody = document.getElementById("cart-sidebar-body");
        cartSidebarBody.innerHTML = "";
    
        let mainProduct = null;  // Keep track of the main product for grouping

        items.forEach(item => {
            if (item.main_product) {
                
                // If it's a main product, create the row for the product
                cartSidebarBody.innerHTML += 
                `
                    <div class="cart-item" data-product-id="${item.id}">
                        <!-- Left Section: Image & Product Info -->
                        <div class="product-info">
                            <img class="product-image" src="${item.image}" alt="${item.name}">
                            <div class="product-details">
                                <span class="product-name">${item.name}</span>
                                <span class="product-price">$${item.total_price}</span>
                            </div>
                        </div>

                        <div class="cart-middle">
                            <div class="quantity-control">
                                <button class="btn-quantity decrease" data-product-id="${item.id}">−</button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="btn-quantity increase" data-product-id="${item.id}">+</button>
                            </div>
                            <div class="item-total-price">
                                <span>$${item.quantity * item.total_price}</span>
                            </div>
                        </div>

                        <!-- Right Section: Remove Button -->
                        <button class="btn-remove" data-product-id="${item.id}">✕</button>
                    </div>
                `;
                mainProduct = item.id;  // Track the main product ID
            } else {
                // If it's an addon, display it under the main product
                if (item.main_product_id === mainProduct) {
                    cartSidebarBody.innerHTML += `
                        <div class="cart-item addon-row" data-product-id="${item.id}">
                            <!-- Left Section: Image & Product Info -->
                            <div class="product-info">
                                <img class="product-image" src="${item.image_url}" alt="${item.name}">
                                <div class="product-details">
                                    <span class="product-name">${item.name}</span>
                                    <span class="product-price">$${item.total_price}</span>
                                </div>
                            </div>

                            <!-- Middle Section: Quantity Controls -->
                            <div class="quantity-control">
                                <span class="quantity">${item.quantity}</span>
                            </div>

                            <!-- Right Section: Remove Button -->
                            <button class="btn-remove" data-product-id="${item.id}">✕</button>
                        </div>
                    `;
                }
            }
        });

    
        document.querySelector(".cart-total").innerText = `$${total}`;
        attachQuantityButtons();
    }
    function attachQuantityButtons() {
        document.querySelectorAll(".increase").forEach(button => {
            button.addEventListener("click", function () {
                updateCartItem(this.dataset.productId, "increase");
            });
        });
    
        document.querySelectorAll(".decrease").forEach(button => {
            button.addEventListener("click", function () {
                updateCartItem(this.dataset.productId, "decrease");
            });
        });
    
        document.querySelectorAll(".btn-remove").forEach(button => {
            button.addEventListener("click", function () {
                removeCartItem(this.dataset.productId);
            });
        });
    }

    function updateCartItem(productId, action) {
        fetch(`/cart/update/${productId}/${action}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchCartData(); // Refresh sidebar cart
            }
        });
    }
    
    function removeCartItem(productId) {
        fetch(`/cart/remove/${productId}/`, {
            method: "GET",
        })
        .then(() => {
            fetchCartData(); // Refresh sidebar cart
        });
    }

    document.querySelectorAll(".btn-quantity").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const action = this.classList.contains("increase") ? "increase" : "decrease";
            const productId = this.dataset.productId;

            // Make an AJAX request to update the cart
            fetch(`/cart/update/${productId}/${action}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the quantity in the UI
                    const quantityElement = this.closest('tr').querySelector('.quantity');
                    const totalPriceElement = this.closest('tr').querySelector('.total-price');

                    quantityElement.textContent = data.quantity;
                    totalPriceElement.textContent = `$${parseFloat(data.total_price).toFixed(2)}`;

                    // Ensure cart total is a valid number before updating UI
                    if (!isNaN(parseFloat(data.cart_total))) {
                        document.querySelector(".cart-total").textContent = `$${parseFloat(data.cart_total).toFixed(2)}`;
                    } else {
                        console.error("Invalid cart total:", data.cart_total);
                    }
                }
            })
            .catch(error => console.error("Error updating cart:", error));
        });
    });

    // ✅ Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ✅ Fetch cart data when the page loads
    fetchCartData();
});