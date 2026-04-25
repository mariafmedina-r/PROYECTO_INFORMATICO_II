import React, { useEffect, useRef } from 'react';

const PaymentModal = ({ amount, isOpen, onClose, onPaymentSuccess, onPaymentError, payerEmail }) => {
    const cardBrickContainerRef = useRef(null);
    const mpInstance = useRef(null);
    const bricksBuilder = useRef(null);

    useEffect(() => {
        if (!isOpen) return;

        const publicKey = import.meta.env.VITE_MERCADOPAGO_PUBLIC_KEY;
        
        if (!window.MercadoPago) {
            console.error("MercadoPago SDK not loaded");
            return;
        }

        // Initialize Mercado Pago
        if (!mpInstance.current) {
            mpInstance.current = new window.MercadoPago(publicKey);
            bricksBuilder.current = mpInstance.current.bricks();
        }

        const renderCardBrick = async (bricksBuilder) => {
            const settings = {
                initialization: {
                    amount: amount,
                    payer: {
                        email: payerEmail || 'test@test.com',
                    },
                },
                customization: {
                    visual: {
                        style: {
                            theme: 'default',
                        },
                    },
                },
                callbacks: {
                    onReady: () => {
                        console.log("Card Brick ready");
                    },
                    onSubmit: async (formData) => {
                        return new Promise((resolve, reject) => {
                            fetch('http://localhost:8000/payments/process', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(formData),
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'approved') {
                                    onPaymentSuccess(data);
                                    resolve();
                                } else {
                                    onPaymentError(data);
                                    reject();
                                }
                            })
                            .catch(error => {
                                onPaymentError(error);
                                reject();
                            });
                        });
                    },
                    onError: (error) => {
                        console.error("Brick Error:", error);
                        onPaymentError(error);
                    },
                },
            };

            window.cardBrickController = await bricksBuilder.create(
                'cardPayment',
                'cardPaymentBrick_container',
                settings
            );
        };

        renderCardBrick(bricksBuilder.current);

        return () => {
            if (window.cardBrickController) {
                window.cardBrickController.unmount();
            }
        };
    }, [isOpen, amount, payerEmail]);

    if (!isOpen) return null;

    return (
        <div className="payment-modal-overlay">
            <div className="payment-modal-content">
                <div className="payment-modal-header">
                    <h2 className="serif">Finalizar Pago Seguro</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>
                <div className="payment-modal-body">
                    <div id="cardPaymentBrick_container"></div>
                </div>
                <div className="payment-modal-footer">
                    <p style={{fontSize: '0.75rem', color: '#999', textAlign: 'center'}}>
                        Tus pagos están protegidos por Mercado Pago. <br/>
                        <b>Modo Simulación Activo</b>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default PaymentModal;
