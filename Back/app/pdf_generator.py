from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime
from typing import Optional
from app.models import ShareIssuance, ShareholderProfile
from app.config import settings


class PDFCertificateGenerator:
    def __init__(self):
        self.font_config = FontConfiguration()
        self.company_name = settings.company_name
        self.company_address = settings.company_address
        self.company_email = settings.company_email
        self.company_website = settings.company_website

    def generate_certificate_html(self, issuance: ShareIssuance, shareholder: ShareholderProfile) -> str:
        """Generate HTML content for the share certificate"""
        issuance_date = issuance.issuance_date.strftime("%B %d, %Y")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Share Certificate</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%), 
                                linear-gradient(-45deg, #f8f9fa 25%, transparent 25%), 
                                linear-gradient(45deg, transparent 75%, #f8f9fa 75%), 
                                linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
                    background-size: 20px 20px;
                    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                }}
                .certificate {{
                    background: white;
                    padding: 40px;
                    border: 3px solid #2c3e50;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    position: relative;
                    min-height: 600px;
                }}
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 120px;
                    color: rgba(0,0,0,0.05);
                    font-weight: bold;
                    z-index: 1;
                    pointer-events: none;
                }}
                .content {{
                    position: relative;
                    z-index: 2;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .company-name {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .company-details {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 5px;
                }}
                .certificate-title {{
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                    margin: 30px 0;
                    color: #2c3e50;
                }}
                .certificate-number {{
                    text-align: right;
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 20px;
                }}
                .main-content {{
                    margin: 30px 0;
                    line-height: 2;
                }}
                .shareholder-name {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 20px;
                }}
                .certificate-text {{
                    font-size: 16px;
                    text-align: justify;
                    margin-bottom: 30px;
                }}
                .share-details {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-left: 4px solid #2c3e50;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .detail-value {{
                    color: #333;
                }}
                .signature-section {{
                    margin-top: 50px;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature-box {{
                    text-align: center;
                    width: 45%;
                }}
                .signature-line {{
                    border-top: 1px solid #333;
                    margin-top: 50px;
                    margin-bottom: 10px;
                }}
                .signature-title {{
                    font-size: 14px;
                    color: #666;
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="certificate">
                <div class="watermark">CERTIFICATE</div>
                <div class="content">
                    <div class="header">
                        <div class="company-name">{self.company_name}</div>
                        <div class="company-details">{self.company_address}</div>
                        <div class="company-details">Email: {self.company_email}</div>
                        <div class="company-details">Website: {self.company_website}</div>
                    </div>
                    
                    <div class="certificate-number">
                        Certificate Number: {issuance.certificate_number}
                    </div>
                    
                    <div class="certificate-title">
                        SHARE CERTIFICATE
                    </div>
                    
                    <div class="main-content">
                        <div class="shareholder-name">
                            {shareholder.first_name} {shareholder.last_name}
                        </div>
                        
                        <div class="certificate-text">
                            This is to certify that the above-named shareholder is the registered owner of the following shares in {self.company_name}, a company duly incorporated and existing under the laws of the jurisdiction in which it operates.
                        </div>
                        
                        <div class="share-details">
                            <div class="detail-row">
                                <span class="detail-label">Number of Shares:</span>
                                <span class="detail-value">{issuance.number_of_shares:,}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Price per Share:</span>
                                <span class="detail-value">${issuance.price_per_share:,.2f}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Total Value:</span>
                                <span class="detail-value">${issuance.total_value:,.2f}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Issuance Date:</span>
                                <span class="detail-value">{issuance_date}</span>
                            </div>
                        </div>
                        
                        <div class="certificate-text">
                            This certificate is issued in accordance with the company's articles of incorporation and bylaws. The shares represented by this certificate are fully paid and non-assessable.
                        </div>
                    </div>
                    
                    <div class="signature-section">
                        <div class="signature-box">
                            <div class="signature-line"></div>
                            <div class="signature-title">Authorized Signature</div>
                        </div>
                        <div class="signature-box">
                            <div class="signature-line"></div>
                            <div class="signature-title">Company Seal</div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>This certificate is computer-generated and is valid without a physical signature when issued through the company's authorized system.</p>
                        <p>Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def generate_certificate_pdf(self, issuance: ShareIssuance, shareholder: ShareholderProfile) -> bytes:
        """Generate PDF certificate for a share issuance"""
        html_content = self.generate_certificate_html(issuance, shareholder)
        
        # Create HTML document
        html_doc = HTML(string=html_content)
        
        # Generate PDF
        pdf_bytes = html_doc.write_pdf(
            font_config=self.font_config,
            optimize_images=True
        )
        
        return pdf_bytes 