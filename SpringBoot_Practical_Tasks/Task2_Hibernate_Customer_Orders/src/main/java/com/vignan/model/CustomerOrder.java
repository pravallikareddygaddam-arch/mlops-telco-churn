package com.vignan.model;

import jakarta.persistence.*;

@Entity
@Table(name = "customer_orders")
public class CustomerOrder {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String product;
    private Double amount;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    protected CustomerOrder() {}
    public CustomerOrder(String product, Double amount) { this.product = product; this.amount = amount; }
    public void setCustomer(Customer customer) { this.customer = customer; }
    public Long getId() { return id; }
    public String getProduct() { return product; }
    public Double getAmount() { return amount; }
    @Override public String toString() {
        return "Order{id=" + id + ", product='" + product + "', amount=" + amount + "}";
    }
}
