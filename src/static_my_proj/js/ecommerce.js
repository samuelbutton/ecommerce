$(document).ready(function () {
    // Contact Form
    var contactForm = $(".contact-form")
    var contactFormMethod = contactForm.attr("method")
    var contactFormEndpoint = contactForm.attr("action")



    function displaySubmitting(submitBtn, defaultText, doSubmit) {
        if (doSubmit) {
            submitBtn.addClass("disabled")
            submitBtn.html("<i class='fa fa-spin fa-spinner'></i> Sending...")
        } else {
            submitBtn.removeClass("disabled")
            submitBtn.html(defaultText)
        }
    }

    contactForm.submit(function (event) {
        event.preventDefault()
        var contactFormData = contactForm.serialize()
        var thisForm = $(this)

        var contactFormSubmitBtn = contactForm.find("[type='submit']")
        var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()

        displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, true)
        $.ajax({
            method: contactFormMethod,
            url: contactFormEndpoint,
            data: contactFormData,
            success: function (data) {
                console.log(data)
                thisForm[0].reset()
                $.alert({
                    title: "Success!",
                    content: data.message,
                    theme: "modern",
                })
                setTimeout(function () {
                    displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
                }, 500)
            },
            error: function (errorData) {
                console.log("error")
                console.log(errorData)

                var jsonData = $.parseJSON(errorData.responseText)
                var msg = ""

                $.each(jsonData, function (key, value) {
                    msg += key + ": " + value[0].message + "<br />"
                })
                $.alert({
                    title: "oops",
                    content: msg,
                    theme: "modern",
                })
                setTimeout(function () {
                    displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
                }, 500)
            }


        })
    })

    // Auto Search
    var searchForm = $(".search-form")
    var searchInput = searchForm.find("[name='q']") // input name='q'
    var typingTimer;
    var typingInterval = 1500
    var searchBtn = searchForm.find("[type='submit']")

    searchInput.keyup(function (event) {
        clearTimeout(typingTimer)
        typingTimer = setTimeout(performSearch, typingInterval)
    })

    searchInput.keydown(function (event) {
        clearTimeout(typingTimer)
    })

    function displaySearching() {
        searchBtn.addClass("disabled")
        searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching...")
    }

    function performSearch() {
        displaySearching()
        query = searchInput.val()
        setTimeout(function () {
            window.location.href = "/search/?q=" + query
        }, 1000)
    }

    // cart + add products
    var productForm = $(".form-product-ajax")
    productForm.submit(function (event) {
        event.preventDefault()
        var thisForm = $(this)
        // var actionEndpoint = thisForm.attr("action")
        var actionEndpoint = thisForm.attr("data-endpoint")
        var method = thisForm.attr("method")
        var formData = thisForm.serialize()
        $.ajax({
            url: actionEndpoint,
            method: method,
            data: formData,
            success: function (data) {
                var submitSpan = $(".submit-span")
                if (data.added) {
                    submitSpan.html('In cart<button type="submit" class="btn btn-link">Remove?</button>')
                } else {
                    submitSpan.html('<button type="submit" class="btn btn-success">Add to cart</button>')
                }
                var navBarCount = $(".navbar-cart-count")
                navBarCount.text(data.countCartItems)
                if (window.location.href.indexOf("cart") != -1) {
                    refreshCart()
                }
            },
            error: function (errorData) {
                $.alert({
                    title: "oops",
                    content: "An error occurred",
                    theme: "modern",
                })
                console.log("error")
                console.log(errorData)
            }
        })
    })

    function refreshCart() {
        console.log("in cart")
        var cartTable = $(".cart-table")
        var cartBody = cartTable.find(".cart-body")
        var productRows = cartBody.find(".cart-product")
        var currentUrl = window.location.href
        // cartBody.html("<h1>Changed</h1>")

        var refreshCartUrl = "/api/cart/";
        var refreshCartMethod = "GET"
        var data = {};

        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function (data) {
                console.log("success")
                console.log(data)

                var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                if (data.products.length > 0) {
                    productRows.html(" ")
                    $.each(data.products, function (index, value) {
                        var newCartItemRemoveForm = hiddenCartItemRemoveForm.clone()
                        newCartItemRemoveForm.css("display", "block")
                        newCartItemRemoveForm.find(".cart-item-product-id").val(value.id)
                        cartBody.prepend("<tr><th scope=\"row\">" + (data.products.length - index)
                            + "</th><td><a href='" + value.url + "''>"
                            + value.name + "</a>" + newCartItemRemoveForm.html() + "</td><td>" + value.price + "</td></tr>")
                    })

                    var cartSubtotal = $(".cart-subtotal")
                    cartSubtotal.text(data.subtotal)
                    var cartTotal = $(".cart-total")
                    cartTotal.text(data.total)
                } else {
                    window.location.href = currentUrl
                }
            },
            error: function (errorData) {
                $.alert({
                    title: "oops",
                    content: "An error occurred",
                    theme: "modern",
                })
                console.log("error")
                console.log(errorData)
            }
        })
    }
})