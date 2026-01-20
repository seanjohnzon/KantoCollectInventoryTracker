"""Local web UI for inventory management dashboard."""

from __future__ import annotations

import json
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select

from app.db import create_db_and_tables, get_engine, get_session_factory
from app.services.reporting import get_item_counts
from app.services.allocation import get_allocation_summary


def _database_url_from_path(db_path: Optional[str]) -> Optional[str]:
    """
    Convert a database path into a SQLite SQLAlchemy URL.

    Args:
        db_path (Optional[str]): Database path or None to use defaults.

    Returns:
        Optional[str]: SQLAlchemy URL or None to use default settings.
    """
    if not db_path:
        return None
    resolved = Path(db_path).expanduser()
    return f"sqlite+pysqlite:///{resolved}"


class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory dashboard."""

    def log_message(self, format: str, *args) -> None:
        """Override to suppress request logging."""
        pass

    def do_GET(self) -> None:
        """
        Handle GET requests for dashboard and API endpoints.
        """
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_dashboard()
        elif path == "/api/items":
            self._serve_items()
        elif path == "/api/allocations":
            self._serve_allocations()
        elif path.startswith("/images/"):
            self._serve_image()
        else:
            self.send_error(404)

    def _get_db_path(self) -> Optional[str]:
        """Extract DB path from query string."""
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        return qs.get("db", [None])[0]

    def _serve_dashboard(self) -> None:
        """
        Serve the main dashboard HTML.
        """
        html = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Kanto Collect Inventory</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #0f0f0f;
        color: #e0e0e0;
      }
      
      .top-nav {
        background: #1a1a1a;
        border-bottom: 1px solid #2a2a2a;
        padding: 0 20px;
        position: sticky;
        top: 0;
        z-index: 1000;
      }
      .nav-container {
        max-width: 1600px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 15px 0;
      }
      .nav-title {
        font-size: 20px;
        font-weight: 600;
        color: #fff;
        margin-right: auto;
      }
      .nav-tabs {
        display: flex;
        gap: 5px;
      }
      .nav-tab {
        padding: 10px 20px;
        background: transparent;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        color: #888;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
      }
      .nav-tab:hover {
        background: #222;
        color: #fff;
        border-color: #444;
      }
      .nav-tab.active {
        background: #2a2a2a;
        color: #fff;
        border-color: #3a3a3a;
      }
      
      .container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 20px;
      }
      
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
      }
      .stat-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 20px;
      }
      .stat-label {
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
      }
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #fff;
      }
      
      .controls {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        gap: 15px;
        align-items: center;
        flex-wrap: wrap;
      }
      .controls input[type="text"] {
        flex: 1;
        min-width: 250px;
        background: #0f0f0f;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 10px 15px;
        color: #e0e0e0;
        font-size: 14px;
      }
      .controls input[type="text"]::placeholder {
        color: #555;
      }
      
      .set-section {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        margin-bottom: 20px;
        overflow: hidden;
      }
      .set-header {
        background: #0f0f0f;
        padding: 15px 20px;
        border-bottom: 1px solid #2a2a2a;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        user-select: none;
      }
      .set-header:hover {
        background: #151515;
      }
      .set-name {
        font-size: 16px;
        font-weight: 600;
        color: #fff;
      }
      .set-count {
        font-size: 14px;
        color: #888;
      }
      .set-content {
        display: none;
      }
      .set-content.expanded {
        display: block;
      }
      
      table {
        width: 100%;
        border-collapse: collapse;
      }
      thead {
        background: #0f0f0f;
        border-bottom: 1px solid #2a2a2a;
      }
      th {
        text-align: left;
        padding: 12px 20px;
        font-size: 11px;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      td {
        padding: 12px 20px;
        border-bottom: 1px solid #222;
        font-size: 14px;
      }
      tbody tr:hover {
        background: #151515;
      }
      tbody tr:last-child td {
        border-bottom: none;
      }
      
      .loading {
        text-align: center;
        padding: 40px;
        color: #666;
      }
      
      .no-data {
        text-align: center;
        padding: 60px 20px;
        color: #666;
      }
      
      .qty-badge {
        display: inline-block;
        background: #1a3a1a;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
        color: #6c6;
      }
      
      .price-badge {
        display: inline-block;
        background: #3a3a1a;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
        color: #cc6;
      }
      
      .owner-badge {
        display: inline-block;
        background: #1a2a3a;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        color: #6cf;
      }
      
      .total-row {
        background: #1a1a1a !important;
        font-weight: 600;
      }
      
      .view-section {
        display: none;
      }
      .view-section.active {
        display: block;
      }
      
      /* Modal styles */
      .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        align-items: center;
        justify-content: center;
      }
      .modal.show { display: flex; }
      .modal-content {
        background-color: #1a1a1a;
        padding: 30px;
        border-radius: 8px;
        width: 400px;
        max-width: 90%;
        border: 1px solid #333;
      }
      .modal-header {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #fff;
      }
      .modal-body {
        margin-bottom: 20px;
      }
      .form-group {
        margin-bottom: 15px;
      }
      .form-label {
        display: block;
        margin-bottom: 5px;
        color: #888;
        font-size: 14px;
      }
      .form-input, .form-select {
        width: 100%;
        padding: 10px;
        background: #2a2a2a;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        color: #fff;
        font-size: 14px;
      }
      .form-input:focus, .form-select:focus {
        outline: none;
        border-color: #16a34a;
      }
      .modal-footer {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
      }
      .modal-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
      }
      .modal-btn-primary {
        background: #16a34a;
        color: white;
      }
      .modal-btn-primary:hover {
        background: #15803d;
      }
      .modal-btn-secondary {
        background: #444;
        color: white;
      }
      .modal-btn-secondary:hover {
        background: #555;
      }
    </style>
  </head>
  <body>
    <!-- Assign Modal -->
    <div id="assignModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">Assign Item</div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Item:</label>
            <div id="modal-item-name" style="color: #fff; font-weight: 500;"></div>
          </div>
          <div class="form-group">
            <label class="form-label">Available Quantity:</label>
            <div id="modal-available-qty" style="color: #16a34a; font-weight: 600; font-size: 18px;"></div>
          </div>
          <div class="form-group">
            <label class="form-label" for="owner-select">Assign to:</label>
            <select id="owner-select" class="form-select">
              <option value="">-- Select Owner --</option>
              <option value="Cihan">Cihan</option>
              <option value="Nima">Nima</option>
              <option value="Askar">Askar</option>
              <option value="Kanto">Kanto</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" for="assign-qty">Quantity to assign:</label>
            <input type="number" id="assign-qty" class="form-input" min="1" value="1">
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" onclick="closeAssignModal()">Cancel</button>
          <button class="modal-btn modal-btn-primary" onclick="confirmAssign()">Assign</button>
        </div>
      </div>
    </div>
    
    <div class="top-nav">
      <div class="nav-container">
        <div class="nav-title">Kanto Collect Inventory</div>
        <div class="nav-tabs">
          <button class="nav-tab active" onclick="switchView('overview')">Overview</button>
          <button class="nav-tab" onclick="switchView('cihan')">Cihan</button>
          <button class="nav-tab" onclick="switchView('askar')">Askar</button>
          <button class="nav-tab" onclick="switchView('nima')">Nima</button>
          <button class="nav-tab" onclick="switchView('kanto')">Kanto</button>
          <button class="nav-tab" onclick="switchView('unallocated')">Unallocated</button>
        </div>
      </div>
    </div>
    
    <div class="container">
      <!-- Overview Section -->
      <div id="view-overview" class="view-section active">
        <div class="stats-grid" style="margin-top: 20px;">
          <div class="stat-card">
            <div class="stat-label">Total Inventory</div>
            <div class="stat-value" id="stat-total">—</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Allocated</div>
            <div class="stat-value" id="stat-allocated">—</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Unallocated</div>
            <div class="stat-value" id="stat-unallocated">—</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Owners</div>
            <div class="stat-value" id="stat-owners">—</div>
          </div>
        </div>
        
        <div class="set-section">
          <div class="set-header">
            <div class="set-name">Allocation by Owner</div>
          </div>
          <div class="set-content expanded">
            <table>
              <thead>
                <tr>
                  <th>Owner</th>
                  <th>Items</th>
                  <th>Unique Products</th>
                </tr>
              </thead>
              <tbody id="owner-summary">
                <tr><td colspan="3" class="loading">Loading...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Owner-specific sections -->
      <div id="view-cihan" class="view-section"></div>
      <div id="view-askar" class="view-section"></div>
      <div id="view-nima" class="view-section"></div>
      <div id="view-kanto" class="view-section"></div>
      
      <!-- Unallocated Section -->
      <div id="view-unallocated" class="view-section">
        <div class="controls" style="margin-top: 20px;">
          <input type="text" id="search-unallocated" placeholder="Search unallocated items..." />
        </div>
        <div id="unallocated-container">
          <div class="loading">Loading...</div>
        </div>
      </div>
    </div>
    
    <script>
      let allocationsData = null;
      let currentView = 'overview';
      
      async function loadAllocations() {
        try {
          const response = await fetch('/api/allocations');
          allocationsData = await response.json();
          
          // Update overview stats
          document.getElementById('stat-total').textContent = allocationsData.total_inventory.toLocaleString();
          document.getElementById('stat-allocated').textContent = allocationsData.total_allocated.toLocaleString();
          document.getElementById('stat-unallocated').textContent = allocationsData.total_unallocated.toLocaleString();
          document.getElementById('stat-owners').textContent = Object.keys(allocationsData.owner_totals).length;
          
          // Populate owner summary
          const tbody = document.getElementById('owner-summary');
          tbody.innerHTML = Object.entries(allocationsData.owner_totals)
            .sort((a, b) => b[1].count - a[1].count)
            .map(([owner, data]) => `
              <tr style="cursor: pointer;" onclick="switchView('${owner.toLowerCase()}')">
                <td><span class="owner-badge">${owner}</span></td>
                <td><span class="qty-badge">${data.count}</span></td>
                <td>${data.items}</td>
              </tr>
            `).join('');
          
          // Render owner views
          renderOwnerViews();
          renderUnallocatedView();
          
        } catch (err) {
          console.error('Failed to load allocations:', err);
        }
      }
      
      function renderOwnerViews() {
        const owners = ['Cihan', 'Askar', 'Nima', 'Kanto'];
        
        owners.forEach(owner => {
          const items = allocationsData.allocated_items.filter(item => 
            item.allocations.some(a => a.owner === owner)
          );
          
          const ownerAllocs = items.map(item => {
            const alloc = item.allocations.find(a => a.owner === owner);
            return {
              ...item,
              allocated: alloc.quantity,
              unit_cost: alloc.unit_cost,
              total_cost: alloc.quantity * alloc.unit_cost
            };
          }).sort((a, b) => b.allocated - a.allocated);
          
          const totalQty = ownerAllocs.reduce((sum, item) => sum + item.allocated, 0);
          const totalCost = ownerAllocs.reduce((sum, item) => sum + item.total_cost, 0);
          
          const container = document.getElementById(`view-${owner.toLowerCase()}`);
          container.innerHTML = `
            <div class="stats-grid" style="margin-top: 20px;">
              <div class="stat-card">
                <div class="stat-label">Total Items</div>
                <div class="stat-value">${totalQty}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Unique Products</div>
                <div class="stat-value">${ownerAllocs.length}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Total Cost</div>
                <div class="stat-value">$${totalCost.toFixed(2)}</div>
              </div>
            </div>
            
            <div class="set-section">
              <div class="set-header">
                <div class="set-name">${owner}'s Items</div>
                <div class="set-count">${ownerAllocs.length} products • ${totalQty} items</div>
              </div>
              <div class="set-content expanded">
                <table>
                  <thead>
                    <tr>
                      <th>Image</th>
                      <th>Item</th>
                      <th>Quantity</th>
                      <th>Unit Cost</th>
                      <th>Total Cost</th>
                      <th>Set</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${ownerAllocs.map(item => `
                      <tr>
                        <td>
                          ${item.image_url ? 
                            `<img src="${item.image_url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" alt="${item.item_name}" />` : 
                            '<div style="width: 60px; height: 60px; background: #2a2a2a; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #666;">No Image</div>'
                          }
                        </td>
                        <td>${item.item_name}</td>
                        <td><span class="qty-badge">${item.allocated}</span></td>
                        <td><span class="price-badge">$${item.unit_cost.toFixed(2)}</span></td>
                        <td><span class="price-badge">$${item.total_cost.toFixed(2)}</span></td>
                        <td style="color: #888; font-size: 12px;">${item.set_name || 'Other'}</td>
                        <td>
                          <button class="edit-allocated-qty-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-owner="${owner}" data-item="${item.item_name}" data-qty="${item.allocated}" style="padding: 4px 8px; margin-right: 4px; background: #2563eb; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 11px;">Edit Qty</button>
                          <button class="move-to-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-owner="${owner}" data-item="${item.item_name}" data-qty="${item.allocated}" style="padding: 4px 8px; margin-right: 4px; background: #ea580c; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 11px;">Move To</button>
                          <button class="remove-allocation-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-owner="${owner}" data-item="${item.item_name}" style="padding: 4px 8px; background: #dc2626; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 11px;">Remove</button>
                        </td>
                      </tr>
                    `).join('')}
                    <tr class="total-row">
                      <td></td>
                      <td><strong>TOTAL</strong></td>
                      <td><span class="qty-badge">${totalQty}</span></td>
                      <td></td>
                      <td><span class="price-badge">$${totalCost.toFixed(2)}</span></td>
                      <td></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          `;
        });
      }
      
      function renderUnallocatedView() {
        const items = allocationsData.unallocated_items;
        const searchTerm = document.getElementById('search-unallocated')?.value.toLowerCase() || '';
        
        // Group by set
        const bySet = {};
        items.forEach(item => {
          const set = item.set_name || 'Other';
          if (!bySet[set]) bySet[set] = [];
          bySet[set].push(item);
        });
        
        const container = document.getElementById('unallocated-container');
        const filtered = Object.entries(bySet).filter(([setName, items]) => {
          if (!searchTerm) return true;
          return setName.toLowerCase().includes(searchTerm) || 
                 items.some(i => i.item_name.toLowerCase().includes(searchTerm));
        });
        
        if (filtered.length === 0) {
          container.innerHTML = '<div class="no-data">No unallocated items found</div>';
          return;
        }
        
        container.innerHTML = filtered.sort((a, b) => {
          const sumA = a[1].reduce((s, i) => s + i.quantity, 0);
          const sumB = b[1].reduce((s, i) => s + i.quantity, 0);
          return sumB - sumA;
        }).map(([setName, items]) => {
          const setTotal = items.reduce((sum, i) => sum + i.quantity, 0);
          return `
            <div class="set-section">
              <div class="set-header" onclick="toggleSet('unalloc-${setName.replace(/[^a-zA-Z0-9]/g, '_')}')">
                <div class="set-name">${setName}</div>
                <div class="set-count">${items.length} items • ${setTotal} qty</div>
              </div>
              <div class="set-content expanded" id="unalloc-${setName.replace(/[^a-zA-Z0-9]/g, '_')}">
                <table>
                  <thead>
                    <tr>
                      <th>Image</th>
                      <th>Item</th>
                      <th>Unit Cost</th>
                      <th>Quantity</th>
                      <th>Total Value</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${items.sort((a, b) => b.quantity - a.quantity).map(item => `
                      <tr>
                        <td>
                          ${item.image_url ? 
                            `<img src="${item.image_url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" alt="${item.item_name}" />` : 
                            '<div style="width: 60px; height: 60px; background: #2a2a2a; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #666;">No Image</div>'
                          }
                        </td>
                        <td>${item.item_name}</td>
                        <td><span class="price-badge">$${(item.unit_cost || 0).toFixed(2)}</span></td>
                        <td><span class="qty-badge">${item.quantity}</span></td>
                        <td><span class="price-badge">$${((item.unit_cost || 0) * item.quantity).toFixed(2)}</span></td>
                        <td>
                          <button class="edit-qty-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-item="${item.item_name}" data-qty="${item.quantity}" style="padding: 4px 8px; margin-right: 4px; background: #2563eb; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 12px;">Edit Qty</button>
                          <button class="assign-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-item="${item.item_name}" data-qty="${item.quantity}" style="padding: 4px 8px; margin-right: 4px; background: #16a34a; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 12px;">Assign</button>
                          <button class="delete-btn" data-normalized="${item.normalized_name || item.item_name.toLowerCase()}" data-item="${item.item_name}" style="padding: 4px 8px; background: #dc2626; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 12px;">Delete</button>
                        </td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            </div>
          `;
        }).join('');
      }
      
      function toggleSet(id) {
        const element = document.getElementById(id);
        if (element) {
          element.classList.toggle('expanded');
        }
      }
      
      function switchView(view) {
        currentView = view;
        
        // Update nav tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
          tab.classList.remove('active');
        });
        event?.target?.classList.add('active');
        
        // Update view sections
        document.querySelectorAll('.view-section').forEach(section => {
          section.classList.remove('active');
        });
        document.getElementById(`view-${view}`).classList.add('active');
      }
      
      // Event listeners
      document.getElementById('search-unallocated')?.addEventListener('input', renderUnallocatedView);
      
      // Event delegation for dynamically created buttons
      document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-qty-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          const qty = parseInt(e.target.dataset.qty);
          window.editQuantity(normalizedName, itemName, qty);
        } else if (e.target.classList.contains('assign-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          const qty = parseInt(e.target.dataset.qty);
          window.assignItem(normalizedName, itemName, qty);
        } else if (e.target.classList.contains('delete-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          window.deleteItem(normalizedName, itemName);
        } else if (e.target.classList.contains('edit-allocated-qty-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          const owner = e.target.dataset.owner;
          const qty = parseInt(e.target.dataset.qty);
          window.editAllocatedQuantity(normalizedName, itemName, owner, qty);
        } else if (e.target.classList.contains('move-to-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          const owner = e.target.dataset.owner;
          const qty = parseInt(e.target.dataset.qty);
          window.moveItemTo(normalizedName, itemName, owner, qty);
        } else if (e.target.classList.contains('remove-allocation-btn')) {
          const normalizedName = e.target.dataset.normalized;
          const itemName = e.target.dataset.item;
          const owner = e.target.dataset.owner;
          window.removeAllocation(normalizedName, itemName, owner);
        } else if (e.target.id === 'assignModal') {
          // Close modal when clicking outside
          closeAssignModal();
        }
      });
      
      // Edit and assign functions - attach to window for global access
      window.editQuantity = function(normalizedName, displayName, currentQty) {
        const newQty = prompt(`Edit quantity for "${displayName}"\\n\\nCurrent: ${currentQty}\\nEnter new quantity:`, currentQty);
        if (newQty !== null && !isNaN(newQty) && parseInt(newQty) >= 0) {
          updateItemQuantity(normalizedName, parseInt(newQty));
        }
      };
      
      window.assignItem = function(normalizedName, displayName, availableQty) {
        // Store data in modal
        const modal = document.getElementById('assignModal');
        modal.dataset.normalizedName = normalizedName;
        modal.dataset.availableQty = availableQty;
        
        // Populate modal
        document.getElementById('modal-item-name').textContent = displayName;
        document.getElementById('modal-available-qty').textContent = availableQty;
        document.getElementById('assign-qty').value = Math.min(availableQty, 1);
        document.getElementById('assign-qty').max = availableQty;
        document.getElementById('owner-select').value = '';
        
        // Show modal
        modal.classList.add('show');
      };
      
      window.closeAssignModal = function() {
        document.getElementById('assignModal').classList.remove('show');
      };
      
      window.confirmAssign = function() {
        const modal = document.getElementById('assignModal');
        const owner = document.getElementById('owner-select').value;
        const qty = parseInt(document.getElementById('assign-qty').value);
        const normalizedName = modal.dataset.normalizedName;
        const availableQty = parseInt(modal.dataset.availableQty);
        
        if (!owner) {
          alert('Please select an owner');
          return;
        }
        
        if (!qty || qty < 1) {
          alert('Please enter a valid quantity');
          return;
        }
        
        if (qty > availableQty) {
          alert(`Cannot assign ${qty}. Only ${availableQty} available.`);
          return;
        }
        
        assignItemToOwner(normalizedName, owner, qty);
        closeAssignModal();
      };
      
      window.deleteItem = function(normalizedName, displayName) {
        if (!confirm(`Are you sure you want to DELETE all transactions for:\\n\\n"${displayName}"\\n\\nThis cannot be undone!`)) {
          return;
        }
        deleteItemTransactions(normalizedName, displayName);
      };
      
      window.editAllocatedQuantity = function(normalizedName, displayName, owner, currentQty) {
        const newQty = prompt(`Edit allocated quantity for "${displayName}"\\n\\nCurrently assigned to ${owner}: ${currentQty}\\nEnter new quantity:`, currentQty);
        if (newQty !== null && !isNaN(newQty) && parseInt(newQty) >= 0) {
          updateAllocatedQuantity(normalizedName, owner, parseInt(newQty));
        }
      };
      
      window.moveItemTo = function(normalizedName, displayName, fromOwner, qty) {
        const owners = ['Cihan', 'Nima', 'Askar', 'Kanto', 'Unallocated'];
        const availableOwners = owners.filter(o => o !== fromOwner);
        
        const toOwner = prompt(`Move "${displayName}" (${qty} units)\\n\\nFrom: ${fromOwner}\\nTo: ${availableOwners.join(', ')}\\n\\nEnter destination (or "Unallocated" to remove assignment):`, '');
        
        if (!toOwner) return;
        
        if (toOwner.toLowerCase() === 'unallocated') {
          if (confirm(`Remove allocation of ${qty} × "${displayName}" from ${fromOwner}?`)) {
            removeAllocation(normalizedName, fromOwner);
          }
        } else if (availableOwners.map(o => o.toLowerCase()).includes(toOwner.toLowerCase())) {
          const targetOwner = availableOwners.find(o => o.toLowerCase() === toOwner.toLowerCase());
          moveAllocation(normalizedName, fromOwner, targetOwner, qty);
        } else {
          alert('Invalid owner. Must be one of: ' + availableOwners.join(', '));
        }
      };
      
      window.removeAllocation = function(normalizedName, displayName, owner) {
        if (!confirm(`Remove allocation of "${displayName}" from ${owner}?\\n\\nThis will move the item back to unallocated.`)) {
          return;
        }
        removeAllocationFromOwner(normalizedName, owner);
      };
      
      async function updateItemQuantity(itemName, newQty) {
        try {
          const response = await fetch('/api/update-quantity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_name: itemName, quantity: newQty })
          });
          
          if (response.ok) {
            alert('Quantity updated successfully!');
            loadAllocations();
          } else {
            alert('Failed to update quantity');
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      async function assignItemToOwner(itemName, owner, qty) {
        try {
          const response = await fetch('/api/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_name: itemName, owner: owner, quantity: qty })
          });
          
          if (response.ok) {
            alert(`Assigned ${qty} × "${itemName}" to ${owner}`);
            loadAllocations();
          } else {
            const error = await response.json();
            alert('Failed to assign: ' + (error.message || 'Unknown error'));
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      async function deleteItemTransactions(normalizedName, displayName) {
        try {
          const response = await fetch('/api/delete-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_name: normalizedName })
          });
          
          if (response.ok) {
            alert(`Deleted all transactions for "${displayName}"`);
            loadAllocations();
          } else {
            const error = await response.json();
            alert('Failed to delete: ' + (error.message || 'Unknown error'));
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      async function updateAllocatedQuantity(normalizedName, owner, newQty) {
        try {
          const response = await fetch('/api/update-allocated-quantity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ normalized_name: normalizedName, owner: owner, quantity: newQty })
          });
          
          if (response.ok) {
            alert('Allocated quantity updated successfully!');
            loadAllocations();
          } else {
            const error = await response.json();
            alert('Failed to update: ' + (error.message || 'Unknown error'));
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      async function moveAllocation(normalizedName, fromOwner, toOwner, qty) {
        try {
          const response = await fetch('/api/move-allocation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              normalized_name: normalizedName, 
              from_owner: fromOwner, 
              to_owner: toOwner,
              quantity: qty 
            })
          });
          
          if (response.ok) {
            alert(`Moved ${qty} items from ${fromOwner} to ${toOwner}`);
            loadAllocations();
          } else {
            const error = await response.json();
            alert('Failed to move: ' + (error.message || 'Unknown error'));
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      async function removeAllocationFromOwner(normalizedName, owner) {
        try {
          const response = await fetch('/api/remove-allocation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ normalized_name: normalizedName, owner: owner })
          });
          
          if (response.ok) {
            alert('Allocation removed successfully!');
            loadAllocations();
          } else {
            const error = await response.json();
            alert('Failed to remove: ' + (error.message || 'Unknown error'));
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
      
      // Load data on page load
      loadAllocations();
    </script>
  </body>
</html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_items(self) -> None:
        """
        Serve items list as JSON.
        """
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        db_path = qs.get("db", [None])[0]
        title_match = qs.get("title_match", ["custom"])[0]
        include_giveaways = qs.get("include_giveaways", ["true"])[0].lower() in {
            "true",
            "1",
            "yes",
        }

        engine = get_engine(_database_url_from_path(db_path))
        create_db_and_tables(engine)
        session_factory = get_session_factory(engine)

        with session_factory() as session:
            items = get_item_counts(
                session=session,
                group_by_buyer=False,
                include_non_sales=include_giveaways,
                title_match=title_match,
            )

        total = sum(item["quantity_sold"] for item in items)
        response = {"total_items": total, "results": items}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _serve_allocations(self) -> None:
        """
        Serve allocation summary as JSON.
        """
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        db_path = qs.get("db", [None])[0]

        engine = get_engine(_database_url_from_path(db_path))
        create_db_and_tables(engine)
        session_factory = get_session_factory(engine)

        with session_factory() as session:
            summary = get_allocation_summary(session, title_match="custom")
            
            # Convert absolute image paths to relative URLs
            for item in summary.get('allocated_items', []):
                if item.get('image_url'):
                    # Convert to URL-safe path
                    import base64
                    encoded = base64.urlsafe_b64encode(item['image_url'].encode()).decode()
                    item['image_url'] = f"/images/{encoded}"
            
            for item in summary.get('unallocated_items', []):
                if item.get('image_url'):
                    import base64
                    encoded = base64.urlsafe_b64encode(item['image_url'].encode()).decode()
                    item['image_url'] = f"/images/{encoded}"

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(summary).encode("utf-8"))
    
    def _serve_image(self) -> None:
        """
        Serve product images from disk.
        """
        try:
            import base64
            # Extract encoded path from URL
            encoded_path = self.path.split('/images/')[1]
            file_path = base64.urlsafe_b64decode(encoded_path).decode()
            
            from pathlib import Path
            img_path = Path(file_path)
            
            if not img_path.exists():
                self.send_error(404)
                return
            
            # Determine content type
            ext = img_path.suffix.lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            content_type = content_types.get(ext, 'application/octet-stream')
            
            # Read and serve image
            with open(img_path, 'rb') as f:
                image_data = f.read()
            
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(image_data)))
            self.end_headers()
            self.wfile.write(image_data)
        
        except Exception as e:
            self.send_error(500, f"Error serving image: {str(e)}")
    
    def do_POST(self) -> None:
        """
        Handle POST requests for updating quantities and assigning items.
        """
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
        except:
            self.send_error(400, "Invalid JSON")
            return
        
        if path == "/api/update-quantity":
            self._handle_update_quantity(data)
        elif path == "/api/assign":
            self._handle_assign(data)
        elif path == "/api/delete-item":
            self._handle_delete_item(data)
        elif path == "/api/update-allocated-quantity":
            self._handle_update_allocated_quantity(data)
        elif path == "/api/move-allocation":
            self._handle_move_allocation(data)
        elif path == "/api/remove-allocation":
            self._handle_remove_allocation(data)
        else:
            self.send_error(404)
    
    def _handle_update_quantity(self, data: dict) -> None:
        """Update item quantity manually."""
        item_name = data.get('item_name')  # This is now the normalized name
        new_quantity = data.get('quantity')
        
        if not item_name or new_quantity is None:
            self.send_error(400, "Missing item_name or quantity")
            return
        
        try:
            from pathlib import Path
            from sqlalchemy import update
            from app.models import Transaction
            from app.services.reporting import normalize_title
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                # The item_name is already normalized, so just find matches
                normalized_target = item_name.lower()
                
                # Get all transactions and find matches
                all_tx = session.execute(select(Transaction)).scalars().all()
                matching_ids = []
                for tx in all_tx:
                    tx_normalized = normalize_title(tx.listing_title, "custom")
                    if tx_normalized == normalized_target:
                        matching_ids.append(tx.id)
                
                if not matching_ids:
                    self.send_error(404, f"No transactions found for: {item_name}")
                    return
                
                # Update the first transaction with the new total quantity
                # Set others to 0
                for i, tx_id in enumerate(matching_ids):
                    qty = new_quantity if i == 0 else 0
                    session.execute(
                        update(Transaction)
                        .where(Transaction.id == tx_id)
                        .values(quantity_sold=qty)
                    )
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error updating quantity: {str(e)}")
    
    def _handle_assign(self, data: dict) -> None:
        """Assign item to owner."""
        item_name = data.get('item_name')
        owner = data.get('owner')
        quantity = data.get('quantity')
        
        if not item_name or not owner or not quantity:
            self.send_error(400, "Missing item_name, owner, or quantity")
            return
        
        try:
            from pathlib import Path
            from app.models import Allocation
            from app.services.reporting import normalize_title
            from app.services.allocation import get_unit_cost_for_item
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                normalized_name = normalize_title(item_name.lower(), "custom")
                
                # Get unit cost using centralized helper
                unit_cost = get_unit_cost_for_item(session, normalized_name)
                
                # Check if allocation already exists
                existing = session.execute(
                    select(Allocation)
                    .where(Allocation.normalized_item_name == normalized_name)
                    .where(Allocation.owner == owner)
                ).scalar()
                
                if existing:
                    existing.allocated_quantity += quantity
                else:
                    new_alloc = Allocation(
                        normalized_item_name=normalized_name,
                        owner=owner,
                        allocated_quantity=quantity,
                        unit_cost=unit_cost,
                        excel_item_name=item_name
                    )
                    session.add(new_alloc)
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error assigning item: {str(e)}")
    
    def _handle_delete_item(self, data: dict) -> None:
        """Delete all transactions for an item."""
        item_name = data.get('item_name')  # This is the normalized name
        
        if not item_name:
            self.send_error(400, "Missing item_name")
            return
        
        try:
            from pathlib import Path
            from sqlalchemy import delete
            from app.models import Transaction
            from app.services.reporting import normalize_title
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                # The item_name is already normalized
                normalized_target = item_name.lower()
                
                # Find all matching transactions
                all_tx = session.execute(select(Transaction)).scalars().all()
                deleted_count = 0
                
                for tx in all_tx:
                    tx_normalized = normalize_title(tx.listing_title, "custom")
                    if tx_normalized == normalized_target:
                        session.delete(tx)
                        deleted_count += 1
                
                if deleted_count == 0:
                    self.send_error(404, f"No transactions found for: {item_name}")
                    return
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "deleted": deleted_count}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error deleting item: {str(e)}")
    
    def _handle_update_allocated_quantity(self, data: dict) -> None:
        """Update the quantity for an existing allocation."""
        normalized_name = data.get('normalized_name')
        owner = data.get('owner')
        new_quantity = data.get('quantity')
        
        if not normalized_name or not owner or new_quantity is None:
            self.send_error(400, "Missing normalized_name, owner, or quantity")
            return
        
        try:
            from pathlib import Path
            from sqlalchemy import select
            from app.models import Allocation
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                # Find the allocation
                allocation = session.execute(
                    select(Allocation)
                    .where(Allocation.normalized_item_name == normalized_name)
                    .where(Allocation.owner == owner)
                ).scalar_one_or_none()
                
                if not allocation:
                    self.send_error(404, f"Allocation not found for {owner}")
                    return
                
                if new_quantity == 0:
                    # Remove allocation if quantity is 0
                    session.delete(allocation)
                else:
                    allocation.allocated_quantity = new_quantity
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error updating allocated quantity: {str(e)}")
    
    def _handle_move_allocation(self, data: dict) -> None:
        """Move allocation from one owner to another."""
        normalized_name = data.get('normalized_name')
        from_owner = data.get('from_owner')
        to_owner = data.get('to_owner')
        quantity = data.get('quantity')
        
        if not normalized_name or not from_owner or not to_owner:
            self.send_error(400, "Missing normalized_name, from_owner, or to_owner")
            return
        
        try:
            from pathlib import Path
            from sqlalchemy import select
            from app.models import Allocation
            from app.services.allocation import get_unit_cost_for_item
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                # Get the source allocation
                source_alloc = session.execute(
                    select(Allocation)
                    .where(Allocation.normalized_item_name == normalized_name)
                    .where(Allocation.owner == from_owner)
                ).scalar_one_or_none()
                
                if not source_alloc:
                    self.send_error(404, f"Allocation not found for {from_owner}")
                    return
                
                # Remove from source
                session.delete(source_alloc)
                
                # Check if target owner already has an allocation for this item
                target_alloc = session.execute(
                    select(Allocation)
                    .where(Allocation.normalized_item_name == normalized_name)
                    .where(Allocation.owner == to_owner)
                ).scalar_one_or_none()
                
                if target_alloc:
                    # Add to existing allocation
                    target_alloc.allocated_quantity += quantity
                else:
                    # Create new allocation for target owner
                    unit_cost = get_unit_cost_for_item(session, normalized_name)
                    new_alloc = Allocation(
                        normalized_item_name=normalized_name,
                        owner=to_owner,
                        allocated_quantity=quantity,
                        unit_cost=unit_cost,
                        excel_item_name=source_alloc.excel_item_name
                    )
                    session.add(new_alloc)
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error moving allocation: {str(e)}")
    
    def _handle_remove_allocation(self, data: dict) -> None:
        """Remove an allocation entirely."""
        normalized_name = data.get('normalized_name')
        owner = data.get('owner')
        
        if not normalized_name or not owner:
            self.send_error(400, "Missing normalized_name or owner")
            return
        
        try:
            from pathlib import Path
            from sqlalchemy import select, delete
            from app.models import Allocation
            
            db_path = Path("data/inventory.db")
            engine = get_engine(f"sqlite+pysqlite:///{db_path}")
            session_factory = get_session_factory(engine)
            
            with session_factory() as session:
                # Delete the allocation
                result = session.execute(
                    delete(Allocation)
                    .where(Allocation.normalized_item_name == normalized_name)
                    .where(Allocation.owner == owner)
                )
                
                if result.rowcount == 0:
                    self.send_error(404, f"Allocation not found for {owner}")
                    return
                
                session.commit()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            
        except Exception as e:
            self.send_error(500, f"Error removing allocation: {str(e)}")


def main() -> None:
    """
    Start the local UI server.
    """
    port = 5173
    server = ThreadingHTTPServer(("127.0.0.1", port), InventoryHandler)
    print(f"Inventory dashboard running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
