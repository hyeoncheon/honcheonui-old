require 'test_helper'

class ServersControllerTest < ActionController::TestCase
  setup do
    @server = servers(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:servers)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create server" do
    assert_difference('Server.count') do
      post :create, :server => { :desc => @server.desc, :name => @server.name, :op_level => @server.op_level, :op_mode => @server.op_mode, :os_arch => @server.os_arch, :os_build => @server.os_build, :os_id => @server.os_id, :os_kernel => @server.os_kernel, :os_name => @server.os_name, :os_rel => @server.os_rel, :st_uptime => @server.st_uptime, :status => @server.status, :uuid => @server.uuid }
    end

    assert_redirected_to server_path(assigns(:server))
  end

  test "should show server" do
    get :show, :id => @server
    assert_response :success
  end

  test "should get edit" do
    get :edit, :id => @server
    assert_response :success
  end

  test "should update server" do
    put :update, :id => @server, :server => { :desc => @server.desc, :name => @server.name, :op_level => @server.op_level, :op_mode => @server.op_mode, :os_arch => @server.os_arch, :os_build => @server.os_build, :os_id => @server.os_id, :os_kernel => @server.os_kernel, :os_name => @server.os_name, :os_rel => @server.os_rel, :st_uptime => @server.st_uptime, :status => @server.status, :uuid => @server.uuid }
    assert_redirected_to server_path(assigns(:server))
  end

  test "should destroy server" do
    assert_difference('Server.count', -1) do
      delete :destroy, :id => @server
    end

    assert_redirected_to servers_path
  end
end
